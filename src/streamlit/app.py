import streamlit as st

st.set_page_config(page_title="Accident Classifier", layout="wide")

pages = [
    st.Page("views/01_accueil_architecture.py", title="Accueil", default=True),
    st.Page("views/02_donnees_preprocessing.py", title="Données & préprocessing"),
    st.Page("views/github_page.py", title="CI/CD & GitHub Projects"),
    st.Page("views/docker_page.py", title="Docker"),
    st.Page("views/mlflow_page.py", title="MLflow / Entraînement"),
    st.Page("views/airflow_page.py", title="Airflow"),
    st.Page("views/bentoml_page.py", title="BentoML"),
    st.Page("views/nginx_page.py", title="Nginx"),
    st.Page("views/prometheus_page.py", title="Prometheus"),
    st.Page("views/grafana_page.py", title="Grafana"),
    st.Page("views/evidently_page.py", title="Evidently"),
    st.Page("views/prediction_page.py", title="Prédiction"),
]

pg = st.navigation(pages)
pg.run()
