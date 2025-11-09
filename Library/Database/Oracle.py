# import oracledb
from abc import ABC

from Library.Database import DatabaseAPI

class OracleAPI(DatabaseAPI, ABC):

    def __init__(self,
                 host: str = "localhost",
                 port: int = 1521,
                 user: str = None,
                 password: str = None,
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

    def _connect_(self):
        dsn = oracledb.makedsn(
            host=self.host,
            port=self.port,
            service_name=self.database or None
        )
        return oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=dsn,
            autocommit=False
        )
