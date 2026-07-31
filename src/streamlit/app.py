import streamlit as st

st.set_page_config(page_title="Accident Classifier", layout="wide")

pages = [
    st.Page("views/presentation_page.py", title="Présentation", default=True),
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
