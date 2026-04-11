import pymssql
from typing import Callable, Any

from Library.Dataframe.Dataframe import pl
from Library.Database.Database import DatabaseAPI

class MicrosoftDatabaseAPI(DatabaseAPI):

    _ADMIN_: str = "master"
    _PARAMETER_TOKEN_: Callable[[int], str] = staticmethod(lambda i: "%s")

    _CHECK_DATATYPE_MAPPING_: dict = {
        pl.Binary: "varbinary",
        pl.Boolean: "bit",

        pl.Int8: "smallint",
        pl.Int16: "smallint",
        pl.Int32: "int",
        pl.Int64: "bigint",

        pl.UInt8: "int",
        pl.UInt16: "int",
        pl.UInt32: "bigint",
        pl.UInt64: "decimal",

        pl.Float32: "real",
        pl.Float64: "float",
        pl.Decimal: "decimal",

        pl.String: "nvarchar",
        pl.Utf8: "nvarchar",

        pl.Date: "date",
        pl.Time: "time",
        pl.Datetime: "datetime2",
        pl.Duration: "bigint",

        pl.List: "nvarchar",
        pl.Array: "nvarchar",
        pl.Field: "nvarchar",
        pl.Struct: "nvarchar",

        pl.Enum: "nvarchar",
        pl.Categorical: "nvarchar",
        pl.Object: "nvarchar"
    }

    _CREATE_DATATYPE_MAPPING_: dict = {
        pl.Binary: "VARBINARY(MAX)",
        pl.Boolean: "BIT",

        pl.Int8: "SMALLINT",
        pl.Int16: "SMALLINT",
        pl.Int32: "INT",
        pl.Int64: "BIGINT",

        pl.UInt8: "INT",
        pl.UInt16: "INT",
        pl.UInt32: "BIGINT",
        pl.UInt64: "DECIMAL(20, 0)",

        pl.Float32: "REAL",
        pl.Float64: "FLOAT",
        pl.Decimal: "DECIMAL(38, 18)",

        pl.String: "NVARCHAR(MAX)",
        pl.Utf8: "NVARCHAR(MAX)",

        pl.Date: "DATE",
        pl.Time: "TIME",
        pl.Datetime: "DATETIME2",
        pl.Duration: "BIGINT",

        pl.List: "NVARCHAR(MAX)",
        pl.Array: "NVARCHAR(MAX)",
        pl.Field: "NVARCHAR(MAX)",
        pl.Struct: "NVARCHAR(MAX)",

        pl.Enum: "NVARCHAR(MAX)",
        pl.Categorical: "NVARCHAR(MAX)",
        pl.Object: "NVARCHAR(MAX)"
    }

    _DESCRIPTION_DATATYPE_MAPPING_: tuple = (
        (pymssql.STRING, pl.String),
        (pymssql.BINARY, pl.Binary),
        (pymssql.DATETIME, pl.Datetime)
    )

    def __init__(self, *,
                 host: str = "localhost",
                 port: int = 1433,
                 user: str = "master",
                 password: str = "master",
                 admin: bool = False,
                 database: str | None = None,
                 schema: str | None = None,
                 table: str | None = None,
                 legacy: bool = False,
                 migrate: bool = False,
                 autocommit: bool = True) -> None:

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

    def _check_(self, structure: dict | None = None) -> str:
        structure = structure if structure is not None else self._STRUCTURE_
        return ",\n    ".join(
            f"('{name}', '{self._CHECK_DATATYPE_MAPPING_[self._normalize_(dtype)]}')"
            for name, dtype in structure.items()
        )

    def _create_(self, structure: dict | None = None) -> str:
        structure = structure if structure is not None else self._STRUCTURE_
        return ",\n    ".join(
            f'[{name}] {self._CREATE_DATATYPE_MAPPING_[self._normalize_(dtype)]}'
            for name, dtype in structure.items()
        )

    def _driver_(self, admin: bool) -> Any:
        database = self._ADMIN_ if admin or not self.database else self.database
        connection = pymssql.connect(
            server=self._host_,
            port=str(self._port_),
            user=self._user_,
            password=self._password_,
            database=database
        )
        connection.autocommit(self._autocommit_)
        return connection
