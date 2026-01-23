# import oracledb
from typing import Callable

from Library.DataFrame import pl
from Library.Database import DatabaseAPI

class OracleAPI(DatabaseAPI):

    _PARAMETER_TOKEN_: Callable[[int], str] = staticmethod(lambda i: f":{i}")

    _CHECK_DATATYPE_MAPPING_: dict = {
        pl.Binary: "BLOB",
        pl.Boolean: "NUMBER",

        pl.Int8: "NUMBER",
        pl.Int16: "NUMBER",
        pl.Int32: "NUMBER",
        pl.Int64: "NUMBER",
        pl.Int128: "NUMBER",

        pl.UInt8: "NUMBER",
        pl.UInt16: "NUMBER",
        pl.UInt32: "NUMBER",
        pl.UInt64: "NUMBER",

        pl.Float32: "FLOAT",
        pl.Float64: "FLOAT",
        pl.Decimal: "NUMBER",

        pl.Utf8: "VARCHAR2",
        pl.String: "VARCHAR2",

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
        pl.Categories: "VARCHAR2",
        pl.Object: "VARCHAR2",
    }

    _CREATE_DATATYPE_MAPPING_: dict = {
        pl.Binary: "BLOB",
        pl.Boolean: "NUMBER(1)",

        pl.Int8: "NUMBER(3)",
        pl.Int16: "NUMBER(5)",
        pl.Int32: "NUMBER(10)",
        pl.Int64: "NUMBER(19)",
        pl.Int128: "NUMBER(38)",

        pl.UInt8: "NUMBER(3)",
        pl.UInt16: "NUMBER(5)",
        pl.UInt32: "NUMBER(10)",
        pl.UInt64: "NUMBER(20)",

        pl.Float32: "FLOAT(24)",
        pl.Float64: "FLOAT(53)",
        pl.Decimal: "NUMBER(38, 18)",

        pl.Utf8: "VARCHAR2(4000)",
        pl.String: "VARCHAR2(4000)",

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
        pl.Categories: "VARCHAR2(4000)",
        pl.Object: "VARCHAR2(4000)",
    }

    _DESCRIPTION_DATATYPE_MAPPING_: dict = {
        # oracledb.DB_TYPE_BLOB: pl.Binary,
        # oracledb.DB_TYPE_RAW: pl.Binary,
        # oracledb.DB_TYPE_LONG_RAW: pl.Binary,
        # oracledb.DB_TYPE_BOOLEAN: pl.Boolean,

        # oracledb.DB_TYPE_NUMBER: pl.Decimal,
        # oracledb.DB_TYPE_BINARY_FLOAT: pl.Float32,
        # oracledb.DB_TYPE_BINARY_DOUBLE: pl.Float64,

        # oracledb.DB_TYPE_VARCHAR: pl.Utf8,
        # oracledb.DB_TYPE_NVARCHAR: pl.Utf8,
        # oracledb.DB_TYPE_CHAR: pl.Utf8,
        # oracledb.DB_TYPE_NCHAR: pl.Utf8,
        # oracledb.DB_TYPE_LONG: pl.Utf8,
        # oracledb.DB_TYPE_CLOB: pl.Utf8,
        # oracledb.DB_TYPE_NCLOB: pl.Utf8,

        # oracledb.DB_TYPE_DATE: pl.Datetime,
        # oracledb.DB_TYPE_TIMESTAMP: pl.Datetime,
        # oracledb.DB_TYPE_TIMESTAMP_TZ: pl.Datetime,
        # oracledb.DB_TYPE_TIMESTAMP_LTZ: pl.Datetime,

        # oracledb.DB_TYPE_INTERVAL_DS: pl.Duration,
        # oracledb.DB_TYPE_INTERVAL_YM: pl.Utf8,

        # oracledb.DB_TYPE_JSON: pl.Utf8,
        # oracledb.DB_TYPE_ROWID: pl.Utf8,
        # oracledb.DB_TYPE_UROWID: pl.Utf8,
    }

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

    def _check_(self):
        parts = []
        for name, dtype in self._STRUCTURE_.items():
            t = self._CHECK_DATATYPE_MAPPING_[type(dtype)]
            parts.append(f"SELECT '{name}' AS column_name, '{t}' AS data_type FROM dual")
        return "\nUNION ALL\n".join(parts)

    def _create_(self):
        return ",\n    ".join(
            f'"{name}" {self._CREATE_DATATYPE_MAPPING_[type(dtype)]}'
            for name, dtype in self._STRUCTURE_.items()
        )

    def _connect_(self, admin: bool):
        database = "ORCL" if admin else (self.database or None)
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
