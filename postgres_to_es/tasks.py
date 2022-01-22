import psycopg2
from celery import Celery, chain
from celery.schedules import crontab
from psycopg2.extras import DictCursor
from pymongo import MongoClient

from config import BROKER_URL, ES_URI, MONGO_URI, PG_DSN
from extractor import PsqlExtractor
from loader import ElasticLoader
from state import MongoState
from transform import Transform
from utils import list_to_tuple

celery_app = Celery("tasks", broker=BROKER_URL)


@celery_app.task
def serve_state() -> bool:
    """Задача для обслуживания состояния, хронящегося в MondoDB."""

    try:
        with MongoClient(MONGO_URI) as mongo_client:
            serve = MongoState(mongo_client, "storage", "state")
            serve()
    except Exception as e:
        print("Error:", e)
    finally:
        mongo_client.close()
        return True


@celery_app.task
def transform_films_work(previous_task: bool) -> bool:
    """
    Задача для трансформации данных фильмов,
    требующих загрузки и хранения в MondoDB.
    """

    if previous_task is True:
        try:
            with MongoClient(MONGO_URI) as mongo_client, psycopg2.connect(
                **PG_DSN, cursor_factory=DictCursor
            ) as pg_conn:
                pg = PsqlExtractor(pg_conn)
                serve = MongoState(mongo_client, "storage", "state")
                tuple_id = serve.get_id("film_work")
                raw_data = (_ for _ in pg.get_data_by_id(tuple_id))
                make_tf = Transform(raw_data)
                make_tf.record_data()
        except Exception as e:
            print("Error:", e)
        finally:
            mongo_client.close()
            return True


@celery_app.task
def transform_persons(previous_task: bool) -> bool:
    """
    Задача для трансформации данных фильмов, связанных с персонами,
    требующих загрузки и хранения в MondoDB.
    """

    if previous_task is True:
        try:
            with MongoClient(MONGO_URI) as mongo_client, psycopg2.connect(
                **PG_DSN, cursor_factory=DictCursor
            ) as pg_conn:
                pg = PsqlExtractor(pg_conn)
                serve = MongoState(mongo_client, "storage", "state")
                persons_id = pg.get_persons_id(serve.get_id("person"))
                tuple_id = list_to_tuple(persons_id)
                raw_data = (_ for _ in pg.get_data_by_id(tuple_id))
                make_tf = Transform(raw_data)
                make_tf.record_data()
        except Exception as e:
            print("Error:", e)
        finally:
            mongo_client.close()
            return True


@celery_app.task
def transform_genres(previous_task: bool) -> bool:
    """
    Задача для трансформации данных фильмов, связанных с жарнами,
    требующих загрузки и хранения в MondoDB.
    """

    if previous_task is True:
        try:
            with MongoClient(MONGO_URI) as mongo_client, psycopg2.connect(
                **PG_DSN, cursor_factory=DictCursor
            ) as pg_conn:
                pg = PsqlExtractor(pg_conn)
                serve = MongoState(mongo_client, "storage", "state")
                genres_id = pg.get_genres_id(serve.get_id("genre"))
                tuple_id = list_to_tuple(genres_id)
                raw_data = (_ for _ in pg.get_data_by_id(tuple_id))
                make_tf = Transform(raw_data)
                make_tf.record_data()
        except Exception as e:
            print("Error:", e)
        finally:
            mongo_client.close()
            return True


@celery_app.task
def es_load(previous_task: bool) -> None:
    """Задача для загрузки подготовленных данных в Elacticsearch."""

    if previous_task is True:
        load = ElasticLoader(ES_URI, MONGO_URI)
        load()


@celery_app.task
def etl() -> None:
    """Последовательно выполняемые задачи."""

    chain(
        serve_state.s(),
        transform_genres.s(),
        transform_persons.s(),
        transform_films_work.s(),
        es_load.s(),
    ).delay()


@celery_app.on_after_configure.connect
def setup_periodic_taskc(sender, **kwargs):
    """Планировщик запуска ETL (раз в 1 минуту)."""

    sender.add_periodic_task(crontab(minute="*/1"), etl.s())
