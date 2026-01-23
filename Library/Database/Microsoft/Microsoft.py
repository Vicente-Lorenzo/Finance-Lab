# import pymssql
from typing import Callable
from decimal import Decimal
from datetime import date, datetime

from Library.DataFrame import pl
from Library.Database import DatabaseAPI

class MicrosoftAPI(DatabaseAPI):

    _PARAMETER_TOKEN_: Callable[[int], str] = staticmethod(lambda i: "%s")

    _CHECK_DATATYPE_MAPPING_: dict = {
        pl.Binary: "varbinary",
        pl.Boolean: "bit",

        pl.Int8: "smallint",
        pl.Int16: "smallint",
        pl.Int32: "int",
        pl.Int64: "bigint",
        pl.Int128: "decimal",

        pl.UInt8: "int",
        pl.UInt16: "int",
        pl.UInt32: "bigint",
        pl.UInt64: "decimal",

        pl.Float32: "real",
        pl.Float64: "float",
        pl.Decimal: "decimal",

        pl.Utf8: "nvarchar",
        pl.String: "nvarchar",

        pl.Date: "date",
        pl.Time: "time",
        pl.Datetime: "datetime2",
        pl.Duration: "bigint",

        pl.Tuple: "nvarchar",
        pl.List: "nvarchar",
        pl.Array: "nvarchar",
        pl.Field: "nvarchar",
        pl.Struct: "nvarchar",

        pl.Enum: "nvarchar",
        pl.Categorical: "nvarchar",
        pl.Categories: "nvarchar",
        pl.Object: "nvarchar",
    }

    _CREATE_DATATYPE_MAPPING_: dict = {
        pl.Binary: "VARBINARY(MAX)",
        pl.Boolean: "BIT",

        pl.Int8: "SMALLINT",
        pl.Int16: "SMALLINT",
        pl.Int32: "INT",
        pl.Int64: "BIGINT",
        pl.Int128: "DECIMAL(38, 0)",

        pl.UInt8: "INT",
        pl.UInt16: "INT",
        pl.UInt32: "BIGINT",
        pl.UInt64: "DECIMAL(20, 0)",

        pl.Float32: "REAL",
        pl.Float64: "FLOAT",
        pl.Decimal: "DECIMAL(38, 18)",

        pl.Utf8: "NVARCHAR(MAX)",
        pl.String: "NVARCHAR(MAX)",

        pl.Date: "DATE",
        pl.Time: "TIME",
        pl.Datetime: "DATETIME2",
        pl.Duration: "BIGINT",

        pl.Tuple: "NVARCHAR(MAX)",
        pl.List: "NVARCHAR(MAX)",
        pl.Array: "NVARCHAR(MAX)",
        pl.Field: "NVARCHAR(MAX)",
        pl.Struct: "NVARCHAR(MAX)",

        pl.Enum: "NVARCHAR(MAX)",
        pl.Categorical: "NVARCHAR(MAX)",
        pl.Categories: "NVARCHAR(MAX)",
        pl.Object: "NVARCHAR(MAX)",
    }

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
