import json

import backoff
import psycopg2
from config import PG_DSN, list_tables, log_config
from extractor import PsqlExtractor
from loguru import logger
from models import StateMap
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor, DictRow
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger.add(**log_config)


class MongoState:
    """Класс работы с состоянием, хранимым в MondoDB"""

    def __init__(self, client: MongoClient, db: str, collection: str):
        self.client = client
        self.db = self.client[db]
        self.collection = self.db[collection]
        self.tables = list_tables

    @logger.catch
    @backoff.on_exception(backoff.expo, PyMongoError, 10)
    def get_id(self, table_name: str) -> tuple:
        query = {"table_name": table_name, "need_load": True}
        batch = self.collection.find(query)
        result = []
        for row in batch:
            result.append(row["id"])
        return tuple(result)

    @logger.catch
    @backoff.on_exception(backoff.expo, PyMongoError, 10)
    def update_or_add(self, value: DictRow, table: str) -> None:
        """
        Поиск документа в коллекции state, проверка
        актуальности поля updated_at этого документа или
        добавление документа в коллекцию в случае его отсутсвия.
        """

        pg_inst = StateMap(**value)
        pg_inst.table_name = table
        find_id = self.collection.find_one({"id": str(pg_inst.id)})
        if find_id is None:
            as_json = json.loads(pg_inst.json())
            self.collection.insert_one(as_json)
            logger.info(
                f"Добавлена новая запись из таблицы {table} с id: {pg_inst.id}."
            )
        elif str(pg_inst.updated_at) > find_id["updated_at"]:
            self.collection.update_one(
                {"id": str(pg_inst.id)},
                {"$set": {"updated_at": str(pg_inst.updated_at), "need_load": True}},
            )
            logger.info(
                f"Обновлены данные записи из таблицы {table} с id: {pg_inst.id}."
            )

    # @logger.catch
    @backoff.on_exception(backoff.expo, OperationalError, 10)
    def make(self, pg: PsqlExtractor) -> None:
        """
        Анализ записей в Postgres и, при необходимости
        обновление state в MongoDB storage.
        """

        for table in self.tables:
            data = (_ for _ in pg.get_table(table))
            while True:
                try:
                    value = next(data)
                    self.update_or_add(value, table)
                except StopIteration:
                    break

    def __call__(self, *args, **kwargs):
        try:
            with psycopg2.connect(**PG_DSN, cursor_factory=DictCursor) as pg_conn:
                pg = PsqlExtractor(pg_conn=pg_conn)
                self.make(pg)
        except OperationalError as e:
            logger.exception(e)
        finally:
            pg_conn.close()
