# import pymssql
from abc import ABC

from Library.Database import DatabaseAPI

class MicrosoftAPI(DatabaseAPI, ABC):

    def __init__(self,
                 host: str = "localhost",
                 port: int = 1433,
                 user: str = "master",
                 password: str = "master",
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
        database = "master" if admin else (self.database or None)
        connection = pymssql.connect(
            server=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=database
        )
        connection.autocommit(admin)
        return connection
