import json
from typing import Generator

import backoff
from config import MONGO_URI, log_config
from loguru import logger
from models import Index
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from utils import mongo_conn_context

logger.add(**log_config)


class Transform:
    def __init__(self, raw_data: Generator):
        self.raw_data = raw_data

    @backoff.on_exception(backoff.expo, PyMongoError, 10)
    def record_data(self) -> None:
        try:
            with mongo_conn_context(MONGO_URI) as mongo_client:
                db = mongo_client["storage"]
                collection = db["prepared_data"]
                while True:
                    try:
                        value = next(self.raw_data)
                        try:
                            data_for_index = Index(**value)
                            find_id = collection.find_one(
                                {"id": str(data_for_index.id)}
                            )
                            if find_id is None:
                                as_json = json.loads(data_for_index.json())
                                collection.insert_one(as_json)
                                logger.info(
                                    f"Фильм с id: {data_for_index.id} подготовлен."
                                )
                        except ValidationError as err:
                            logger.exception(err)
                    except StopIteration:
                        break
        except Exception as e:
            logger.exception(e)
