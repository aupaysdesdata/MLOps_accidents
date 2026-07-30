import os
import bentoml
import pandas as pd
from pydantic import BaseModel, Field, ConfigDict

with bentoml.importing():
    import mlflow

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
MODEL_URI = "models:/Modèle_Gravité_Accidents@champion"

class InputModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    place: int
    catu: int
    sexe: int
    secu1: float
    year_acc: int
    victim_age: int
    catv: int
    obsm: int
    motor: int
    catr: int
    circ: int
    surf: int
    situ: int
    vma: int
    jour: int
    mois: int
    lum: int
    dep: int
    com: int
    agg_: int
    int_: int = Field(alias="int")
    atm: int
    col: int
    lat: float
    long: float
    hour: int
    nb_victim: int
    nb_vehicules: int


@bentoml.service
class PredictService:
    def __init__(self):
        self.model = mlflow.sklearn.load_model(
            "models:/Modèle_Gravité_Accidents/latest"
        )

    def _load_model(self):
        """Méthode interne pour (re)charger le modèle champion depuis MLflow."""
        try:
            self.model = mlflow.sklearn.load_model(MODEL_URI)
            print(f"Modèle chargé avec succès depuis {MODEL_URI}")
        except Exception as e:
            # Fallback vers 'latest' si l'alias champion n'existe pas encore
            print(f"Échec du chargement de {MODEL_URI} ({e}). Tentative avec 'latest'...")
            self.model = mlflow.sklearn.load_model("models:/Modèle_Gravité_Accidents/latest")

    @bentoml.api(route="/reload_model")
    def reload_model(self) -> dict:
        """Endpoint appelé par Airflow pour rafraîchir le modèle en mémoire."""
        self._load_model()
        return {"status": "success", "message": "Modèle rechargé avec succès"}

    @bentoml.api(route="/predict")
    def predict(self, input_data: InputModel) -> dict:
        feature_names = [
            "place", "catu", "sexe", "secu1", "year_acc", "victim_age",
            "catv", "obsm", "motor", "catr", "circ", "surf", "situ", "vma",
            "jour", "mois", "lum", "dep", "com", "agg_", "int", "atm",
            "col", "lat", "long", "hour", "nb_victim", "nb_vehicules",
        ]
        x = pd.DataFrame(
            [
                [
                    input_data.place,
                    input_data.catu,
                    input_data.sexe,
                    input_data.secu1,
                    input_data.year_acc,
                    input_data.victim_age,
                    input_data.catv,
                    input_data.obsm,
                    input_data.motor,
                    input_data.catr,
                    input_data.circ,
                    input_data.surf,
                    input_data.situ,
                    input_data.vma,
                    input_data.jour,
                    input_data.mois,
                    input_data.lum,
                    input_data.dep,
                    input_data.com,
                    input_data.agg_,
                    input_data.int_,
                    input_data.atm,
                    input_data.col,
                    input_data.lat,
                    input_data.long,
                    input_data.hour,
                    input_data.nb_victim,
                    input_data.nb_vehicules,
                ]
            ],
            columns=feature_names,
            dtype=float,
        )

        pred = self.model.predict(x)
        return {"prediction": pred.tolist()}
