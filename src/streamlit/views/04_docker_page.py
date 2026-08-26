import streamlit as st

st.set_page_config(
    page_title="Docker - Infrastructure",
    page_icon="🐳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .main-header {font-size: 2.8rem; font-weight: bold; color: #0db7ed; margin-bottom: 0.75rem;}
    .sub-header {font-size: 1.5rem; font-weight: 600; color: #333; margin-top: 1.75rem;}
    .service-card {background-color: #f0f8ff; border-left: 5px solid #0db7ed; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="main-header">Docker : infrastructure du projet</p>', unsafe_allow_html=True)
st.markdown(
    "L'ensemble du projet tourne dans des **conteneurs Docker** orchestrés via **Docker Compose**. "
    "Chaque service est isolé, reproductible et peut être lancé d'une seule commande : `docker compose up`."
)

st.divider()

st.markdown('<p class="sub-header">1. Architecture globale</p>', unsafe_allow_html=True)
st.markdown(
    "Le projet compte **13 services** répartis en 4 couches fonctionnelles. "
    "Ils communiquent via le réseau interne Docker (`mlops_accidents_default`) et partagent des **volumes nommés** pour la persistance des données."
)

col1, col2 = st.columns(2)
with col1:
    st.markdown("##### Couche données & ML")
    st.markdown(
        """
        - **`preprocess`** — prépare les données brutes et alimente le volume `accidents-data`
        - **`train`** — entraîne le modèle Random Forest et envoie les métriques à MLflow
        - **`mlflow`** — serveur de tracking des expériences (port 5000)
        """
    )
    st.markdown("##### Couche orchestration")
    st.markdown(
        """
        - **`postgres-airflow`** — base PostgreSQL pour l'état d'Airflow
        - **`airflow-init`** — initialise la BDD et crée l'utilisateur admin (one-shot)
        - **`airflow`** — scheduler + webserver Airflow (port 8080)
        """
    )

with col2:
    st.markdown("##### Couche API & exposition")
    st.markdown(
        """
        - **`ml-api`** — service BentoML qui sert les prédictions (port interne 3000)
        - **`streamlit`** — cette application de présentation (port interne 8501)
        - **`nginx`** — reverse proxy HTTPS, point d'entrée unique (ports 80/443)
        - **`nginx-exporter`** — exporte les métriques nginx pour Prometheus (port 9113)
        """
    )
    st.markdown("##### Couche observabilité")
    st.markdown(
        """
        - **`prometheus`** — collecte les métriques (port 9090)
        - **`grafana`** — dashboards de monitoring (port 3000)
        - **`grafana-init`** — configure alertes et contact points au démarrage (one-shot)
        """
    )

st.divider()

st.markdown('<p class="sub-header">2. Volumes partagés</p>', unsafe_allow_html=True)
st.markdown("Les volumes permettent aux services de **partager des données sans couplage direct**.")

volumes = {
    "accidents-data": "Données préprocessées (X_train, X_test, y_train, y_test). Écrit par `preprocess`, lu par `train`, `airflow` et le service de drift.",
    "postgres-airflow-data": "État persistant d'Airflow (DAGs, runs, logs de tâches).",
    "airflow-logs": "Logs des tâches Airflow, montés dans le conteneur pour consultation.",
    "prometheus_data": "Séries temporelles Prometheus, conservées entre redémarrages.",
    "grafana_data": "Dashboards et configuration Grafana.",
}

for name, desc in volumes.items():
    st.markdown(
        f"<div class='service-card'><strong>{name}</strong> — {desc}</div>",
        unsafe_allow_html=True,
    )

st.divider()

st.markdown('<p class="sub-header">3. Images construites sur mesure</p>', unsafe_allow_html=True)
st.markdown(
    "Quatre services utilisent un **Dockerfile dédié** plutôt qu'une image publique, "
    "pour embarquer le code et les dépendances du projet :"
)

st.code(
    """
# Lancer tout le projet
docker compose up --build

# Images construites localement :
# - Dockerfile.airflow       → service airflow + airflow-init
# - src/preprocess/Dockerfile → service preprocess
# - src/train/Dockerfile      → service train
# - src/bentoml/Dockerfile    → service ml-api
# - src/streamlit/Dockerfile  → service streamlit
# - src/nginx/Dockerfile      → service nginx
    """,
    language="bash",
)

st.markdown("### Pourquoi Docker Compose ici ?")
st.info(
    "Docker Compose garantit que tous les services démarrent dans le bon ordre (grâce aux `depends_on` et `healthcheck`), "
    "que les variables d'environnement sont cohérentes, et qu'un nouveau membre de l'équipe peut lancer "
    "l'intégralité du projet en une seule commande, sans installer MLflow, Airflow ou Prometheus localement."
)

st.success(
    "Docker est le socle sur lequel repose toute la reproductibilité du projet : "
    "même environnement en dev, en CI et en production."
)
