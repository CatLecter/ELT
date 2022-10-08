import asyncio
import os

import aiosqlite
import asyncpgsa
from aiosqlite import Error
from dotenv import find_dotenv, load_dotenv
from loguru import logger

from postgres_saver import PostgresSaver
from sqlite_loader import SQLiteLoader

load_dotenv(find_dotenv(filename='.env_postgres'))

logger.add(
    sink="./log/migrate.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="00:00"
)


async def process():
    try:
        async with aiosqlite.connect(
                database='db.sqlite'
        ) as sqlite_conn, asyncpgsa.create_pool(
            host=os.environ.get('POSTGRES_HOST'),
            port=os.environ.get('POSTGRES_PORT'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            database=os.environ.get('POSTGRES_DB'),
        ) as pg_conn:
            data = await SQLiteLoader(sqlite_conn).get_all_data()
            postgres_saver = PostgresSaver(pg_conn)
            await postgres_saver.save_all_data(data)
    except Error as error:
        logger.exception(error)
    finally:
        await pg_conn.close()


if __name__ == '__main__':
    asyncio.run(process())
