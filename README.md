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

## External
### Data.gouv : Jeux de données CSV et API
https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024
[Description des bases de données annuelles](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024?resource_id=8ef4c2a3-91a0-4d98-ae3a-989bde87b62a)

https://www.data.gouv.fr/dataservices/api-tabulaire-data-gouv-fr-beta
L'URL de base de l'API tabulaire est https://tabular-api.data.gouv.fr/api.
Sa documentation technique générale est https://tabular-api.data.gouv.fr/api/doc.

Identifiant de ressource rid pour bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere
- Table des caractéristiques des accidents corporels de la circulation en 2024 en France : rid = 83f0fb0e-e0ef-47fe-93dd-9aaee851674a https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/20251021-115900/caract-2024.csv
- https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/20251021-115812/lieux-2024.csv

Peut-on automatiser l'export des csv, via les url de téléchargement ?
Via l'API tabulaire, comment identifier quand une nouvelle ressource est dispo et surtout comment récupérer le rid qui est propre à chaque csv de chaque année et de chaque type de données (caract, lieux, vehicules, usagers) ?
