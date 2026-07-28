FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances
COPY bentofile.yaml .
RUN pip install --no-cache-dir bentoml mlflow scikit-learn numpy pydantic

# Copie du code
COPY . /app

EXPOSE 3000

CMD ["bentoml", "serve", "service:PredictService", "--port", "3000", "--host", "0.0.0.0"]