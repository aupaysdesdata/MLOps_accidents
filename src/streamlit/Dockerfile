FROM python:3.12-slim

WORKDIR /app

COPY ./src/streamlit/requirement.txt .

RUN pip install -r requirement.txt

COPY ./src/streamlit/. .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
