import json
from typing import Generator

import backoff
from pydantic import ValidationError
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import MONGO_URI
from models import Index


class Transform:
    def __init__(self, raw_data: Generator):
        self.raw_data = raw_data

    @backoff.on_exception(backoff.expo, PyMongoError, 10)
    def record_data(self) -> None:
        try:
            with MongoClient(MONGO_URI) as mongo_client:
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
                                print(f"Фильм с id: {data_for_index.id} подготовлен.")
                        except ValidationError as err:
                            print("Pydantic error:", err)
                    except StopIteration:
                        break
        except Exception as e:
            print("Error:", e)
        finally:
            mongo_client.close()
