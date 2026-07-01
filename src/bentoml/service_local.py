import os
import numpy as np
import mlflow.sklearn
from fastapi import FastAPI
from pydantic import BaseModel, Field

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))

app = FastAPI()
model = mlflow.sklearn.load_model("models:/Modèle_Gravité_Accidents/latest")


class InputModel(BaseModel):
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

    model_config = {"populate_by_name": True}


class PredictRequest(BaseModel):
    input_data: InputModel


@app.post("/predict")
def predict(request: PredictRequest):
    d = request.input_data
    x = np.array([
        d.place, d.catu, d.sexe, d.secu1, d.year_acc, d.victim_age,
        d.catv, d.obsm, d.motor, d.catr, d.circ, d.surf, d.situ, d.vma,
        d.jour, d.mois, d.lum, d.dep, d.com, d.agg_, d.int_, d.atm,
        d.col, d.lat, d.long, d.hour, d.nb_victim, d.nb_vehicules,
    ], dtype=float).reshape(1, -1)

    pred = model.predict(x)
    return {"prediction": pred.tolist()}
