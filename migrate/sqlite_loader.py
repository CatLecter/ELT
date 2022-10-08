from dataclasses import dataclass

import aiosqlite

from schemes import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class SQLiteLoader:
    """Выгрузка данных из БД sqlite."""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn
        self.conn.row_factory = aiosqlite.Row

    async def get_table(self, table_name: str, schema: dataclass):
        """Функция получения данных из БД sqlite
        пачками по 100 записей.
        """

        table = []
        async with self.conn.execute(f'SELECT * FROM {table_name}') as pool:
            while True:
                values = await pool.fetchmany(100)
                if values:
                    for value in values:
                        table.append(schema(*value))
                else:
                    break
        return table

    async def get_all_data(self):
        """Возвращает dict с данными из БД sqlite."""

        return {
            # 'film_work': await self.get_table('film_work', FilmWork),
            'genre': await self.get_table('genre', Genre),
            # 'person': await self.get_table('person', Person),
            # 'genre_film_work': await self.get_table('genre_film_work', GenreFilmWork),
            # 'person_film_work': await self.get_table('person_film_work', PersonFilmWork),
        }
