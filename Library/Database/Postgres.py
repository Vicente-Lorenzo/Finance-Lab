import psycopg2
from abc import ABC

from Library.Database import DatabaseAPI

class PostgresAPI(DatabaseAPI, ABC):

    def __init__(self,
                 host: str = "localhost",
                 port: int = 5432,
                 user: str = "postgres",
                 password: str = "postgres",
                 database: str = None,
                 schema: str = None,
                 table: str = None):

        super().__init__(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            schema=schema,
            table=table
        )

    def _connect_(self, admin: bool):
        database = "postgres" if admin else (self.database or None)
        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=database
        )
        connection.autocommit = admin
        return connection
