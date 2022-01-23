from contextlib import contextmanager

from pymongo import MongoClient


@contextmanager
def mongo_conn_context(mongo_uri: str):
    mongo_client = MongoClient(mongo_uri)
    yield mongo_client
    mongo_client.close()


def list_to_tuple(list_id: list) -> tuple:
    return tuple([str(*_) for _ in list_id])
