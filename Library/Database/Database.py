import polars as pl

from abc import ABC, abstractmethod

from Library.Logging import HandlerAPI
from Library.Database import QueryAPI
from Library.Statistics import Timer

class DatabaseAPI(ABC):

    def __init__(self,
                 host: str = None,
                 port: int = None,
                 user: str = None,
                 password: str = None,
                 database: str = None,
                 schema: str = None,
                 table: str = None):

        self._host = host
        self._port = port
        self._user = user
        self._password = password

        self._database = database
        self._schema = schema
        self._table = table
        self._defaults = {"database": self._database, "schema": self._schema, "table": self._table}

        self._connection = None
        self._cursor = None

        self._log = HandlerAPI(Class=self.__class__.__name__)

    @abstractmethod
    def _connect_(self):
        raise NotImplementedError

    def connect(self):
        try:
            self._connection = self._connect_()
            self._cursor = self._connection.cursor()
            self._log.info(lambda: f"Connected to {self._host}:{self._port}")
            if self._database:
                self._log.debug(lambda: f"Database: {self._database}")
            if self._schema:
                self._log.debug(lambda: f"Schema: {self._schema}")
            if self._table:
                self._log.debug(lambda: f"Table: {self._table}")
        except Exception as e:
            self._log.error(lambda: f"Failed to Connect")
            self._log.exception(lambda: str(e))
            raise e
        return self

    def __enter__(self):
        return self.connect()

    def disconnect(self):
        try:
            if self.indexed():
                self._cursor.close()
            if self.connected():
                self._connection.close()
            self._log.info(lambda: f"Disconnected from {self._host}:{self._port}")
        except Exception as e:
            self._log.error(lambda: f"Failed to Disconnect")
            self._log.exception(lambda: str(e))
            raise e
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type or exception_value or exception_traceback:
            self._log.exception(lambda: f"Exception type: {exception_type}")
            self._log.exception(lambda: f"Exception value: {exception_value}")
            self._log.exception(lambda: f"Traceback: {exception_traceback}")
        return self.disconnect()

    def connected(self) -> bool:
        return self._connection is not None

    def indexed(self) -> bool:
        return self._cursor is not None

    def _query_(self, query: QueryAPI, **kwargs) -> str:
        return query(**{**self._defaults, **kwargs})

    def commit(self):
        if self.connected():
            timer = Timer()
            timer.start()
            self._connection.commit()
            timer.stop()
            self._log.debug(lambda: f"Transaction commit ({timer.result()})")
        return self

    def rollback(self):
        if self.connected():
            timer = Timer()
            timer.start()
            self._connection.rollback()
            timer.stop()
            self._log.debug(lambda: f"Transaction rollback ({timer.result()})")
        return self

    def _execute_(self, execute) -> None:
        if not self.connected():
            self.connect()
        try:
            timer = Timer()
            timer.start()
            execute()
            timer.stop()
            self._log.debug(lambda: f"Executed Query ({timer.result()})")
        except Exception as e:
            self.rollback()
            self._log.error(lambda: "Failed to Execute Query")
            raise e

    def execute(self, query: QueryAPI, *args, **kwargs):
        self._execute_(lambda: self._cursor.execute(self._query_(query, **kwargs), *args))
        return self

    def executemany(self, query: QueryAPI, *args, **kwargs):
        self._execute_(lambda: self._cursor.executemany(self._query_(query, **kwargs), *args))
        return self

    def _fetch_(self, fetch) -> pl.DataFrame:
        if not self.connected():
            self.connect()
        try:
            timer = Timer()
            timer.start()
            rows = fetch()
            columns = [desc[0] for desc in self._cursor.description] if self._cursor.description else []
            df = pl.DataFrame(rows, schema=columns, orient="row")
            timer.stop()
            self._log.debug(lambda: f"Fetched Query ({timer.result()}): {len(df)} data points")
            return df
        except Exception as e:
            self.rollback()
            self._log.error(lambda: "Failed to Fetch Query")
            raise e

    def fetchone(self) -> pl.DataFrame:
        return self._fetch_(lambda: self._cursor.fetchone())

    def fetchmany(self, n: int) -> pl.DataFrame:
        return self._fetch_(lambda: self._cursor.fetchmany(n))

    def fetchall(self) -> pl.DataFrame:
        return self._fetch_(lambda: self._cursor.fetchall())

    def __del__(self):
        if self.connected():
            self.disconnect()
