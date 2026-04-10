import oracledb
from typing import Callable

from Library.Dataframe.Dataframe import pl
from Library.Database.Database import DatabaseAPI

class OracleDatabaseAPI(DatabaseAPI):

    _ADMIN_: str = "ORCL"
    _PARAMETER_TOKEN_: Callable[[int], str] = staticmethod(lambda i: f":{i}")

    _CHECK_DATATYPE_MAPPING_: dict = {
        pl.Binary: "BLOB",
        pl.Boolean: "NUMBER",

        pl.Int8: "NUMBER",
        pl.Int16: "NUMBER",
        pl.Int32: "NUMBER",
        pl.Int64: "NUMBER",

        pl.UInt8: "NUMBER",
        pl.UInt16: "NUMBER",
        pl.UInt32: "NUMBER",
        pl.UInt64: "NUMBER",

        pl.Float32: "FLOAT",
        pl.Float64: "FLOAT",
        pl.Decimal: "NUMBER",

        pl.String: "VARCHAR2",
        pl.Utf8: "VARCHAR2",

        pl.Date: "DATE",
        pl.Time: "INTERVAL DAY TO SECOND",
        pl.Datetime: "TIMESTAMP",
        pl.Duration: "INTERVAL DAY TO SECOND",

        pl.List: "VARCHAR2",
        pl.Array: "VARCHAR2",
        pl.Field: "VARCHAR2",
        pl.Struct: "VARCHAR2",

        pl.Enum: "VARCHAR2",
        pl.Categorical: "VARCHAR2",
        pl.Object: "VARCHAR2"
    }

    _CREATE_DATATYPE_MAPPING_: dict = {
        pl.Binary: "BLOB",
        pl.Boolean: "NUMBER(1)",

        pl.Int8: "NUMBER(3)",
        pl.Int16: "NUMBER(5)",
        pl.Int32: "NUMBER(10)",
        pl.Int64: "NUMBER(19)",

        pl.UInt8: "NUMBER(3)",
        pl.UInt16: "NUMBER(5)",
        pl.UInt32: "NUMBER(10)",
        pl.UInt64: "NUMBER(20)",

        pl.Float32: "FLOAT(24)",
        pl.Float64: "FLOAT(53)",
        pl.Decimal: "NUMBER(38, 18)",

        pl.String: "VARCHAR2(4000)",
        pl.Utf8: "VARCHAR2(4000)",

        pl.Date: "DATE",
        pl.Time: "INTERVAL DAY TO SECOND",
        pl.Datetime: "TIMESTAMP",
        pl.Duration: "INTERVAL DAY TO SECOND",

        pl.List: "VARCHAR2(4000)",
        pl.Array: "VARCHAR2(4000)",
        pl.Field: "VARCHAR2(4000)",
        pl.Struct: "VARCHAR2(4000)",

        pl.Enum: "VARCHAR2(4000)",
        pl.Categorical: "VARCHAR2(4000)",
        pl.Object: "VARCHAR2(4000)"
    }

    _DESCRIPTION_DATATYPE_MAPPING_: tuple = (
        (oracledb.STRING, pl.String),
        (oracledb.BINARY, pl.Binary),
        (oracledb.DATETIME, pl.Datetime)
    )

    def __init__(self, *,
                 host: str = "localhost",
                 port: int = 1521,
                 user: str = "ORCL",
                 password: str = "ORCL",
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

    def _check_(self, structure: dict = None):
        structure = structure if structure is not None else self._STRUCTURE_
        parts = []
        for name, dtype in structure.items():
            t = self._CHECK_DATATYPE_MAPPING_[self._normalize_(dtype)]
            parts.append(f"SELECT '{name}' AS column_name, '{t}' AS data_type FROM dual")
        return "\nUNION ALL\n".join(parts)

    def _create_(self, structure: dict = None):
        structure = structure if structure is not None else self._STRUCTURE_
        return ",\n    ".join(
            f'"{name}" {self._CREATE_DATATYPE_MAPPING_[self._normalize_(dtype)]}'
            for name, dtype in structure.items()
        )

    def _driver_(self, admin: bool):
        database = self._ADMIN_ if admin or not self.database else self.database
        dsn = oracledb.makedsn(
            host=self._host_,
            port=self._port_,
            service_name=database
        )
        connection = oracledb.connect(
            user=self._user_,
            password=self._password_,
            dsn=dsn
        )
        connection.autocommit = self._autocommit_
        return connection
