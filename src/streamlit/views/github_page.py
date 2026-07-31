import streamlit as st

st.title("CI/CD & Gestion de projet (GitHub)")

st.markdown(
    """
Le développement du projet s'appuie sur deux fonctionnalités de **GitHub** :
l'**intégration continue** (GitHub Actions), qui vérifie automatiquement chaque
changement de code, et **GitHub Projects**, qui organise le suivi des tâches
de l'équipe sous forme de tableau Kanban.
"""
)

st.divider()
st.subheader("Intégration continue (GitHub Actions)")

st.markdown(
    """
Le workflow `.github/workflows/ci.yml` se déclenche sur chaque `push` (toutes
branches) et sur chaque *pull request* vers `main`. Il enchaîne deux jobs :
"""
)

ci_jobs = [
    {
        "Job": "compile-check",
        "Déclencheur": "push sur une branche ≠ main",
        "Rôle": "Vérifie que tous les fichiers .py du dossier src compilent (python -m py_compile)",
    },
    {
        "Job": "docker-build",
        "Déclencheur": "pull request vers main (après compile-check)",
        "Rôle": "Build de toutes les images du projet via docker compose build",
    },
]

st.dataframe(ci_jobs, use_container_width=True, hide_index=True)

st.code(
    """name: CI

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]

jobs:
  compile-check:
    if: github.ref != 'refs/heads/master'
    steps:
      - run: python -m py_compile $(find src -name "*.py")

  docker-build:
    if: github.event_name == 'pull_request'
    needs: compile-check
    steps:
      - run: docker compose build
""",
    language="yaml",
)

st.markdown(
    """
    a completer
    """
)

st.link_button(
    "Voir les exécutions CI (GitHub Actions)",
    "https://github.com/aupaysdesdata/MLOps_accidents/actions",
    use_container_width=True,
)

st.divider()
st.subheader("Gestion de projet (GitHub Projects)")

st.markdown(
    """
    a completer
    """
)

st.link_button(
    "Ouvrir le board GitHub Projects",
    "https://github.com/aupaysdesdata/MLOps_accidents/projects",
    use_container_width=True,
)
