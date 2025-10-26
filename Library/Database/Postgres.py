import psycopg2

from Library.Database import DatabaseAPI

class PostgresAPI(DatabaseAPI):

    def __init__(self,
                 host: str = "localhost",
                 port: int = 5432,
                 user: str = None,
                 password: str = None,
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

    def _connect_(self):
        return psycopg2.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            dbname=self._database or None,
            autocommit=False
        )
