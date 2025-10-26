# import oracledb

from Library.Database import DatabaseAPI

class OracleAPI(DatabaseAPI):

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
            host=self._host,
            port=self._port,
            service_name=self._database or None
        )
        return oracledb.connect(
            user=self._user,
            password=self._password,
            dsn=dsn,
            autocommit=False
        )
