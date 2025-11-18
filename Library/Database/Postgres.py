import psycopg2
import polars as pl

from Library.Database import DatabaseAPI

class PostgresAPI(DatabaseAPI):

    DESCRIPTION_DATATYPE_MAPPING = {
        16: pl.Boolean,
        20: pl.Int64,
        21: pl.Int16,
        23: pl.Int32,
        700: pl.Float32,
        701: pl.Float64,
        1700: pl.Float64,
        25: pl.Utf8,
        1043: pl.Utf8,
        1082: pl.Date,
        1114: pl.Datetime,
        1184: pl.Datetime
    }

    def __init__(self,
                 host: str = "localhost",
                 port: int = 5432,
                 user: str = "postgres",
                 password: str = "postgres",
                 admin: bool = False,
                 database: str = None,
                 schema: str = None,
                 table: str = None,
                 migrate: bool = False):

        super().__init__(
            host=host,
            port=port,
            user=user,
            admin=admin,
            password=password,
            database=database,
            schema=schema,
            table=table,
            migrate=migrate
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
