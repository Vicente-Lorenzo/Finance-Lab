# import pymssql
from datetime import date, datetime
from decimal import Decimal

from Library.DataFrame import pl
from Library.Database import DatabaseAPI

class MicrosoftAPI(DatabaseAPI):

    DESCRIPTION_DATATYPE_MAPPING = {
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
