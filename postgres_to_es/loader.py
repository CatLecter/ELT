import json

import backoff
from config import log_config
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchException
from elasticsearch.helpers import bulk
from loguru import logger
from models import Index
from pymongo.errors import PyMongoError
from urllib3.exceptions import HTTPError
from utils import mongo_conn_context

logger.add(**log_config)


class ElasticLoader:
    """Класс загрузки данных в Elasticsearch."""

    def __init__(self, es_host: str, mongo_host: str):
        self.es_host = es_host
        self.mongo_host = mongo_host
        self.index_name = "movies"

    @backoff.on_exception(backoff.expo, PyMongoError, 10)
    def get_bulk(self) -> list:
        try:
            with mongo_conn_context(self.mongo_host) as mongo_client:
                db = mongo_client["storage"]
                collection = db["prepared_data"]
                data = collection.find()
                result = [Index(**_).dict() for _ in data]
                return result
        except PyMongoError as e:
            logger.exception(e)

    @backoff.on_exception(backoff.expo, PyMongoError, 10)
    def update_state(self, list_id: list) -> None:
        try:
            with mongo_conn_context(self.mongo_host) as mongo_client:
                db = mongo_client["storage"]
                collection = db["state"]
                for _ in list_id:
                    collection.update_one(
                        {"id": str(_["id"])},
                        {"$set": {"need_load": False}},
                    )
        except PyMongoError as e:
            logger.exception(e)

    @backoff.on_exception(backoff.expo, PyMongoError, 10)
    def del_by_id(self, list_id: list) -> None:
        try:
            with mongo_conn_context(self.mongo_host) as mongo_client:
                db = mongo_client["storage"]
                collection = db["prepared_data"]
                for _ in list_id:
                    collection.delete_one({"id": str(_["id"])})
        except PyMongoError as e:
            logger.exception(e)

    @backoff.on_exception(backoff.expo, (ElasticsearchException, HTTPError), 10)
    def load(self) -> None:
        try:
            prepared_bulk = self.get_bulk()
            with Elasticsearch(hosts=self.es_host) as client:
                bulk(
                    client=client,
                    actions=[
                        {"_index": self.index_name, "_id": film["id"], **film}
                        for film in prepared_bulk
                    ],
                )
        except ElasticsearchException as e:
            logger.exception(e)
        finally:
            self.update_state(prepared_bulk)
            self.del_by_id(prepared_bulk)
            client.close()
            logger.info(f"Данные загружены в Elasticsearch.")

    @backoff.on_exception(backoff.expo, (ElasticsearchException, HTTPError), 10)
    def create_index(self) -> None:
        try:
            with Elasticsearch(hosts=self.es_host) as client:
                with open("indexes/movies.json", "r") as f:
                    _index = json.load(f)
                    client.indices.create(
                        index="movies",
                        body=_index,
                        ignore=400,
                    )
        except ElasticsearchException as e:
            logger.exception(e)
        finally:
            client.close()

    def __call__(self, *args, **kwargs):
        self.create_index()
        self.load()
