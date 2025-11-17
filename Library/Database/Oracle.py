# import oracledb
import polars as pl
from abc import ABC

from Library.Database import DatabaseAPI

class OracleAPI(DatabaseAPI, ABC):

    DESCRIPTION_DATATYPE_MAPPING = {
        # oracledb.DB_TYPE_NUMBER: pl.Float64,
        # oracledb.DB_TYPE_VARCHAR: pl.Utf8,
        # oracledb.DB_TYPE_CHAR: pl.Utf8,
        # oracledb.DB_TYPE_NVARCHAR: pl.Utf8,
        # oracledb.DB_TYPE_NCHAR: pl.Utf8,
        # oracledb.DB_TYPE_DATE: pl.Datetime,
        # oracledb.DB_TYPE_TIMESTAMP: pl.Datetime,
    }

    def __init__(self,
                 host: str = "localhost",
                 port: int = 1521,
                 user: str = "ORCL",
                 password: str = "ORCL",
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

    def _connect_(self, admin: bool):
        database = "ORCL" if admin else (self.database or None)
        dsn = oracledb.makedsn(
            host=self.host,
            port=self.port,
            service_name=database
        )
        connection = oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=dsn
        )
        connection.autocommit = False
        return connection
