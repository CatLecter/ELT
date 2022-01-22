import os

from dotenv import load_dotenv

load_dotenv()


PG_DSN = {
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": "postgres",
    "port": os.environ.get("POSTGRES_PORT"),
    "options": "-c search_path=content",
}

list_tables = ["film_work", "genre", "person"]

mongo_user = os.environ.get("MONGO_USER")
mongo_password = os.environ.get("MONGO_PASSWORD")
mongo_host = os.environ.get("MONGO_HOST")
mongo_port = os.environ.get("MONGO_PORT")
# MONGO_URI = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/storage?authSource=admin"
MONGO_URI = os.environ.get("MONGO_URL")

BROKER_URL = os.environ.get("BROKER_URL")

es_host = os.environ.get("ES_HOST")
es_port = os.environ.get("ES_PORT")

# ES_URI = f"{es_host}:{es_port}"
ES_URI = os.environ.get("ES_URL")
