Project Name
==============================

This project is a starting Pack for MLOps projects based on the subject "road accident". It's not perfect so feel free to make some modifications on it.

Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── logs               <- Logs from training and predicting
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   ├── check_structure.py    
    │   │   ├── import_raw_data.py 
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── visualization  <- Scripts to create exploratory and results oriented visualizations
    │   │   └── visualize.py
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py

---------

## Steps to follow 

Convention : All python scripts must be run from the root specifying the relative file path.

### 1- Create a virtual environment using Virtualenv.

    `python -m venv my_env`

###   Activate it 

    `./my_env/Scripts/activate`

###   Install the packages from requirements.txt

    `pip install -r .\requirements.txt` ### You will have an error in "setup.py" but this won't interfere with the rest

### 2- Execute import_raw_data.py to import the 4 datasets.

    `python .\src\data\import_raw_data.py` ### It will ask you to create a new folder, accept it.

### 3- Execute make_dataset.py initializing `./data/raw` as input file path and `./data/preprocessed` as output file path.

    `python .\src\data\make_dataset.py`

### 4- Execute train_model.py to instanciate the model in joblib format

    `python .\src\models\train_model.py`

### 5- Finally, execute predict_model.py with respect to one of these rules :
  
  - Provide a json file as follow : 

    
    `python ./src/models/predict_model.py ./src/models/test_features.json`

  test_features.json is an example that you can try 

  - If you do not specify a json file, you will be asked to enter manually each feature. 

------------------------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

------------------------

# Data

## Raw

The original, immutable data dump.
Le jeu de données est fourni et hebergé par Datascientest.
Il correspond aux données annuelles 2021 des accidents corporels de la circulation routiere fournis par Data.gouv. 

# MLOps accidents

Ce dépôt met en place un pipeline MLOps pour classer la gravité d’un accident de la route à partir de données ouvertes. Le projet combine preprocessing, entraînement de modèle, suivi d’expériences avec MLflow, exposition d’une API de prédiction et une interface Streamlit.

## Vue d’ensemble

Le flux actuel du projet est le suivant :

- ingestion et préparation des données issues du dossier [data/raw](data/raw)
- création de jeux de données train/test dans [data/preprocessed](data/preprocessed)
- entraînement d’un modèle Random Forest dans [src/train/train_model.py](src/train/train_model.py)
- enregistrement des métriques et du modèle dans MLflow
- prédiction via une API et une interface utilisateur Streamlit

## Structure du projet

- [data/raw](data/raw) : fichiers CSV bruts des années 2021 à 2024
- [data/preprocessed](data/preprocessed) : données préparées utilisées pour l’entraînement
- [data/archives](data/archives) : copies de jeux de données historiques
- [src/preprocess/preprocess.py](src/preprocess/preprocess.py) : fusion et transformation des datasets
- [src/train/train_model.py](src/train/train_model.py) : entraînement du modèle et logging MLflow
- [src/streamlit/app.py](src/streamlit/app.py) : application web de démonstration
- [src/bentoml/service.py](src/bentoml/service.py) : service de prédiction basé sur BentoML
- [docker-compose.yml](docker-compose.yml) : orchestration de MLflow, entraînement, API et interface
- [mlruns](mlruns) : artefacts et métadonnées MLflow

## Prérequis

- Python 3.10+
- Docker et Docker Compose
- (optionnel) conda ou virtualenv

## Démarrage rapide

### 1. Créer un environnement Python

```bash
python -m venv .venv
source .venv/bin/activate
```

Sous Windows PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Installer les dépendances

```bash
pip install -r src/preprocess/requirements.txt
pip install -r src/train/requirements.txt
pip install -r src/streamlit/requirements.txt
```

### 3. Préparer les données

```bash
python src/preprocess/preprocess.py
```

Cette étape produit les fichiers CSV dans [data/preprocessed](data/preprocessed).

### 4. Entraîner le modèle

```bash
python src/train/train_model.py
```

Le script entraîne un Random Forest et enregistre les métriques suivantes dans MLflow :

- accuracy
- precision
- recall
- f1_score

Le modèle est également enregistré sous le nom de registre : Modèle_Gravité_Accidents.

### 5. Lancer l’application localement

Pour l’interface Streamlit :

```bash
streamlit run src/streamlit/app.py
```

## Déploiement avec Docker

Le projet peut être lancé dans son ensemble via Docker Compose :

```bash
docker compose up --build
```

Le compose inclut :

- MLflow sur le port 5000
- l’entraînement du modèle
- une API de prédiction
- une interface Streamlit
- un reverse proxy Nginx

## Expérience MLflow

Les runs sont visibles dans l’interface MLflow à l’adresse suivante :

```text
http://localhost:5000
```

## Notes importantes

- Les données utilisées par le modèle sont celles présentes dans [data/preprocessed](data/preprocessed).
- Le modèle de référence est actuellement un Random Forest.
- Les prédictions sont envoyées depuis [src/streamlit/app.py](src/streamlit/app.py) vers l’API de prédiction configurée via la variable d’environnement MODEL_API_URL.

## Sources de données

Les jeux de données utilisés sont issus des bases publiques relatives aux accidents corporels de la circulation routière, disponibles via les fichiers fournis dans [data/raw](data/raw). Plus d'infos dans : [references\data_sources.md](references\data_sources.md).