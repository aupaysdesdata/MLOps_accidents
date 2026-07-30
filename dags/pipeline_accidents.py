from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowFailException
from docker.types import Mount
import mlflow
from airflow.utils.trigger_rule import TriggerRule
from mlflow.tracking import MlflowClient
import requests
import os
import re
from pathlib import Path


DATA_VOLUME_NAME = os.getenv("DATA_VOLUME_NAME", "mlops_accidents_accidents-data")
MLFLOW_TRACKING_URI = "http://mlflow:5000"
EXPERIMENT_NAME = "Gravité_Accidents"
MODEL_NAME = "Modèle_Gravité_Accidents"
DOCKER_NETWORK = "mlops_accidents_default"

MAX_DROP_ALLOWED = 0.05


default_args = {
    "owner": "mlops_team",
    "start_date": datetime(2026, 1, 1),
    "retries": 1,
}


def check_metrics_and_alert(**context):
    """
    Récupère le f1_score du dernier run de l'expérience 'Gravité_Accidents'
    et le valide avant d'autoriser la mise en production.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if not experiment:
        raise AirflowFailException(
            f"L'expérience '{EXPERIMENT_NAME}' n'a pas été trouvée dans MLflow."
        )

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["attributes.start_time DESC"],
        max_results=1,
    )

    if not runs:
        raise AirflowFailException(
            f"Aucun run trouvé pour l'expérience {EXPERIMENT_NAME}."
        )

    current_run = runs[0]
    current_f1 = current_run.data.metrics.get("f1_score")
    current_run_id = current_run.info.run_id

    context["ti"].xcom_push(key="current_run_id", value=current_run_id)
    print(
        f"Nouveau modèle entraîné détecté - Run ID: {current_run_id} | F1-Score: {current_f1}"
    )

    if current_f1 is None:
        raise AirflowFailException(
            "Le dernier run MLflow n'a pas enregistré de métrique 'f1_score'."
        )

    try:
        prod_model_version = client.get_model_version_by_alias(MODEL_NAME, "champion")
        prod_run = client.get_run(prod_model_version.run_id)
        prod_f1 = prod_run.data.metrics.get("f1_score")

        if prod_f1 and (prod_f1 - current_f1) > MAX_DROP_ALLOWED:
            raise AirflowFailException(
                f"ALERTE : Dégradation majeure des performances. "
                f"Prod F1: {prod_f1:.3f} VS Nouveau F1: {current_f1:.3f}. Déploiement annulé."
            )
        print(f"Validation réussie par rapport à la Prod (F1 Prod: {prod_f1:.3f})")
    except mlflow.exceptions.MlflowException:
        print("Aucun modèle marqué '@champion' trouvé. Première promotion du projet.")


def promote_model_to_champion(**context):
    """
    Associe l'alias 'champion' à la dernière version du modèle validé.
    Le conteneur ml-api (BentoML) se basera sur cet alias pour servir l'interface Streamlit.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    run_id = context["ti"].xcom_pull(key="current_run_id", task_ids="evaluate_metrics")

    filter_string = f"run_id='{run_id}'"
    versions = client.search_model_versions(filter_string)

    if not versions:
        raise AirflowFailException(
            f"Aucune version de modèle trouvée dans le Registry pour le run {run_id}."
        )

    latest_version = versions[0].version

    client.set_registered_model_alias(MODEL_NAME, "champion", latest_version)
    print(
        f"Succès : Le modèle '{MODEL_NAME}' version {latest_version} est maintenant désigné comme '@champion'."
    )


def reload_predict_service():
    """
    Déclenche un appel vers le conteneur d'API (ml-api) pour recharger
    en mémoire la version associée à l'alias '@champion'.
    """
    bento_url = "http://ml-api:3000/reload_model"
    try:
        response = requests.post(bento_url, timeout=15)
        response.raise_for_status()
        print("Le conteneur 'ml-api' a mis à jour son modèle avec succès.")
    except Exception as e:
        raise AirflowFailException(f"Échec du rechargement de ml-api : {e}")


with DAG(
    "mlops_accident_gravity_pipeline",
    default_args=default_args,
    description="Pipeline d'entraînement pour la gravité des accidents",
    schedule="@monthly",
    catchup=False,
    tags=["accidents"],
) as dag:
    # task_make_dataset = DockerOperator(
    #     task_id='docker_make_dataset',
    #     image='make_dataset:latest',
    #     api_version='auto',
    #     auto_remove=True,
    #     network_mode=DOCKER_NETWORK,
    #     mounts=[Mount(source=f"{BASE_DIR}/mlruns", target="/app/mlruns", type="bind")]
    # )

    task_preprocess = DockerOperator(
        task_id="preprocess",
        image="mlops_accidents-preprocess:latest",
        api_version="auto",
        auto_remove=True,
        mount_tmp_dir=False,
        network_mode=DOCKER_NETWORK,
        mounts=[Mount(source=f"{DATA_VOLUME_NAME}", target="/app/data", type="volume")],
    )

    task_train = DockerOperator(
        task_id="train",
        image="mlops_accidents-train:latest",
        api_version="auto",
        auto_remove=True,
        mount_tmp_dir=False,
        network_mode=DOCKER_NETWORK,
        environment={"MLFLOW_TRACKING_URI": MLFLOW_TRACKING_URI},
        mounts=[Mount(source=f"{DATA_VOLUME_NAME}", target="/app/data", type="volume")],
    )

    task_evaluate = PythonOperator(
        task_id="evaluate_metrics",
        python_callable=check_metrics_and_alert,
    )

    task_promote = PythonOperator(
        task_id="promote_model",
        python_callable=promote_model_to_champion,
    )

    task_reload = PythonOperator(
        task_id="reload_predict_service",
        python_callable=reload_predict_service,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    task_preprocess >> task_train >> task_evaluate
    task_evaluate >> task_promote
    task_evaluate >> task_reload
