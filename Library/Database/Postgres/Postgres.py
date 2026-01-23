import psycopg
from typing import Callable

from Library.DataFrame import pl
from Library.Database import DatabaseAPI

class PostgresAPI(DatabaseAPI):

    _PARAMETER_TOKEN_: Callable[[int], str] = staticmethod(lambda i: "%s")

    _DESCRIPTION_DATATYPE_MAPPING_ = {
        16: pl.Boolean,
        21: pl.Int16,
        23: pl.Int32,
        20: pl.Int64,
        700: pl.Float32,
        701: pl.Float64,
        1700: pl.Float64,
        25: pl.Utf8,
        1043: pl.Utf8,
        1082: pl.Date,
        1114: pl.Datetime,
        1184: pl.Datetime
    }

    def __init__(self, *,
                 host: str = "localhost",
                 port: int = 5432,
                 user: str = "postgres",
                 password: str = "postgres",
                 admin: bool = False,
                 database: str = None,
                 schema: str = None,
                 table: str = None,
                 legacy: bool = False,
                 migrate: bool = False,
                 autocommit: bool = True):

        super().__init__(
            host=host,
            port=port,
            user=user,
            admin=admin,
            password=password,
            database=database,
            schema=schema,
            table=table,
            legacy=legacy,
            migrate=migrate,
            autocommit=autocommit
        )

    def _check_(self):
        return ",\n    ".join(
            f"('{name}', '{self._CHECK_DATATYPE_MAPPING_[type(dtype)]}')"
            for name, dtype in self._STRUCTURE_.items()
        )

    def _create_(self):
        return ",\n    ".join(
            f'"{name}" {self._CREATE_DATATYPE_MAPPING_[type(dtype)]}'
            for name, dtype in self._STRUCTURE_.items()
        )

    def _connect_(self, admin: bool):
        database = "postgres" if admin else (self.database or None)
        connection = psycopg.connect(
            host=self._host_,
            port=self._port_,
            user=self._user_,
            password=self._password_,
            dbname=database
        )
        connection.autocommit = self._autocommit_
        return connection
