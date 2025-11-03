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
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database or None,
            autocommit=False
        )
