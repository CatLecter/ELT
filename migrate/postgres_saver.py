import dataclasses


class PostgresSaver:
    """Загрузка данных в БД postgres."""

    def __init__(self, pg_conn):
        self.pg_conn = pg_conn

    async def save_all_data(self, data: dataclasses):
        """Функция сохранения всех данных из таблиц
        в БД postgres пачками по 100 записей.
        """

        for table_name, table_data in data.items():
            values = ', '.join([str(dataclasses.astuple(row)) for row in table_data])
            query = f'INSERT INTO content.{table_name} VALUES {values} ' \
                    f'ON CONFLICT (id) DO NOTHING;'
            await self.pg_conn.fetch(query)
