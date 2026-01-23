# import pymssql
from typing import Callable
from decimal import Decimal
from datetime import date, datetime

from Library.DataFrame import pl
from Library.Database import DatabaseAPI

class MicrosoftAPI(DatabaseAPI):

    _PARAMETER_TOKEN_: Callable[[int], str] = staticmethod(lambda i: "%s")

    _DESCRIPTION_DATATYPE_MAPPING_ = {
        int: pl.Int64,
        float: pl.Float64,
        bool: pl.Boolean,
        str: pl.Utf8,
        date: pl.Date,
        datetime: pl.Datetime,
        Decimal: pl.Float64
    }

    def __init__(self, *,
                 host: str = "localhost",
                 port: int = 1433,
                 user: str = "master",
                 password: str = "master",
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
            password=password,
            admin=admin,
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
            f'[{name}] {self._CREATE_DATATYPE_MAPPING_[type(dtype)]}'
            for name, dtype in self._STRUCTURE_.items()
        )

    def _connect_(self, admin: bool):
        database = "master" if admin else (self.database or None)
        connection = pymssql.connect(
            server=self._host_,
            port=self._port_,
            user=self._user_,
            password=self._password_,
            database=database
        )
        connection.autocommit(self._autocommit_)
        return connection
