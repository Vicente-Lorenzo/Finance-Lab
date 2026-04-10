import psycopg
from typing import Callable

from Library.Dataframe.Dataframe import pl
from Library.Database.Database import DatabaseAPI

class PostgresDatabaseAPI(DatabaseAPI):

    _ADMIN_: str = "postgres"
    _PARAMETER_TOKEN_: Callable[[int], str] = staticmethod(lambda i: "%s")

    _CHECK_DATATYPE_MAPPING_: dict = {
        pl.Binary: "bytea",
        pl.Boolean: "boolean",

        pl.Int8: "smallint",
        pl.Int16: "smallint",
        pl.Int32: "integer",
        pl.Int64: "bigint",

        pl.UInt8: "integer",
        pl.UInt16: "integer",
        pl.UInt32: "bigint",
        pl.UInt64: "numeric",

        pl.Float32: "real",
        pl.Float64: "double precision",
        pl.Decimal: "numeric",

        pl.String: "character varying",
        pl.Utf8: "character varying",

        pl.Date: "date",
        pl.Time: "time without time zone",
        pl.Datetime: "timestamp without time zone",
        pl.Duration: "interval",

        pl.List: "character varying",
        pl.Array: "character varying",
        pl.Field: "character varying",
        pl.Struct: "character varying",

        pl.Enum: "character varying",
        pl.Categorical: "character varying",
        pl.Object: "character varying"
    }

    _CREATE_DATATYPE_MAPPING_: dict = {
        pl.Binary: "BYTEA",
        pl.Boolean: "BOOLEAN",

        pl.Int8: "SMALLINT",
        pl.Int16: "SMALLINT",
        pl.Int32: "INTEGER",
        pl.Int64: "BIGINT",

        pl.UInt8: "INTEGER",
        pl.UInt16: "INTEGER",
        pl.UInt32: "BIGINT",
        pl.UInt64: "NUMERIC",

        pl.Float32: "REAL",
        pl.Float64: "DOUBLE PRECISION",
        pl.Decimal: "NUMERIC",

        pl.String: "VARCHAR",
        pl.Utf8: "VARCHAR",

        pl.Date: "DATE",
        pl.Time: "TIME",
        pl.Datetime: "TIMESTAMP",
        pl.Duration: "INTERVAL",

        pl.List: "VARCHAR",
        pl.Array: "VARCHAR",
        pl.Field: "VARCHAR",
        pl.Struct: "VARCHAR",

        pl.Enum: "VARCHAR",
        pl.Categorical: "VARCHAR",
        pl.Object: "VARCHAR"
    }

    _DESCRIPTION_DATATYPE_MAPPING_: tuple = (
        (psycopg.STRING, pl.String),
        (psycopg.BINARY, pl.Binary),
        (psycopg.DATETIME, pl.Datetime)
    )

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

    def _check_(self, structure: dict = None):
        structure = structure if structure is not None else self._STRUCTURE_
        return ",\n    ".join(
            f"('{name}', '{self._CHECK_DATATYPE_MAPPING_[self._normalize_(dtype)]}')"
            for name, dtype in structure.items()
        )

    def _create_(self, structure: dict = None):
        structure = structure if structure is not None else self._STRUCTURE_
        return ",\n    ".join(
            f'"{name}" {self._CREATE_DATATYPE_MAPPING_[self._normalize_(dtype)]}'
            for name, dtype in structure.items()
        )

    def _driver_(self, admin: bool):
        database = self._ADMIN_ if admin or not self.database else self.database
        connection = psycopg.connect(
            host=self._host_,
            port=self._port_,
            user=self._user_,
            password=self._password_,
            dbname=database
        )
        connection.autocommit = self._autocommit_
        return connection
