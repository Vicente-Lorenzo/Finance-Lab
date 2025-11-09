import polars as pl
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_width_chars(-1)
pl.Config.set_fmt_str_lengths(1000)
pl.Config.set_fmt_table_cell_list_len(-1)

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

        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.database = database
        self.schema = schema
        self.table = table
        self.defaults = {"database": self.database, "schema": self.schema, "table": self.table}

        self.connection = None
        self.cursor = None

        self._log_ = HandlerAPI(Class=self.__class__.__name__)

    @abstractmethod
    def _connect_(self):
        raise NotImplementedError

    def connected(self) -> bool:
        return self.connection is not None

    def cursored(self) -> bool:
        return self.cursor is not None

    def commit(self):
        if self.connected():
            timer = Timer()
            timer.start()
            self.connection.commit()
            timer.stop()
            self._log_.debug(lambda: f"Commit Operation ({timer.result()})")
        return self

    def rollback(self):
        if self.connected():
            timer = Timer()
            timer.start()
            self.connection.rollback()
            timer.stop()
            self._log_.debug(lambda: f"Rollback Operation ({timer.result()})")
        return self

    def connect(self):
        try:
            if self.connected() and self.cursored():
                return self
            if self.connected() or self.cursored():
                self.disconnect()
            timer = Timer()
            timer.start()
            self.connection = self._connect_()
            self.cursor = self.connection.cursor()
            if self.database:
                self._log_.debug(lambda: f"Database: {self.database}")
            if self.schema:
                self._log_.debug(lambda: f"Schema: {self.schema}")
            if self.table:
                self._log_.debug(lambda: f"Table: {self.table}")
            timer.stop()
            self._log_.info(lambda: f"Connected to {self.host}:{self.port} ({timer.result()})")
            return self
        except Exception as e:
            self._log_.error(lambda: f"Failed at Connect Operation")
            self._log_.exception(lambda: str(e))
            raise e

    def __enter__(self):
        return self.connect()

    def disconnect(self):
        try:
            if not self.connected() and not self.cursored():
                return self
            timer = Timer()
            timer.start()
            if self.cursored():
                self.cursor.close()
                self.cursor = None
            self.commit()
            if self.connected():
                self.connection.close()
                self.connection = None
            timer.stop()
            self._log_.info(lambda: f"Disconnected from {self.host}:{self.port} ({timer.result()})")
            return self
        except Exception as e:
            self._log_.error(lambda: f"Failed at Disconnect Operation")
            self._log_.exception(lambda: str(e))
            raise e

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type or exception_value or exception_traceback:
            self._log_.exception(lambda: f"Exception type: {exception_type}")
            self._log_.exception(lambda: f"Exception value: {exception_value}")
            self._log_.exception(lambda: f"Traceback: {exception_traceback}")
        return self.disconnect()

    def _query_(self, query: QueryAPI, **kwargs) -> str:
        return query(**{**self.defaults, **kwargs})

    def _execute_(self, execute):
        try:
            self.connect()
            timer = Timer()
            timer.start()
            execute()
            timer.stop()
            self._log_.debug(lambda: f"Execute Operation ({timer.result()})")
            return self
        except Exception as e:
            self.rollback()
            self._log_.error(lambda: "Failed at Execute Operation")
            raise e

    def execute(self, query: QueryAPI, *args, **kwargs):
        return self._execute_(lambda: self.cursor.execute(self._query_(query, **kwargs), args if args else None))

    def executemany(self, query: QueryAPI, *args, **kwargs):
        return self._execute_(lambda: self.cursor.executemany(self._query_(query, **kwargs), args if args else None))

    def _fetch_(self, fetch) -> pl.DataFrame:
        try:
            self.connect()
            timer = Timer()
            timer.start()
            rows = fetch()
            rows = rows if any(isinstance(row, tuple) for row in rows) else [rows] if rows else []
            columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
            df = pl.DataFrame(rows, schema=columns, orient="row")
            timer.stop()
            self._log_.debug(lambda: f"Fetch Operation ({timer.result()}): {len(df)} data points")
            return df
        except Exception as e:
            self.rollback()
            self._log_.error(lambda: "Failed at Fetch Operation")
            raise e

    def fetchone(self) -> pl.DataFrame:
        return self._fetch_(lambda: self.cursor.fetchone())

    def fetchmany(self, n: int) -> pl.DataFrame:
        return self._fetch_(lambda: self.cursor.fetchmany(n))

    def fetchall(self) -> pl.DataFrame:
        return self._fetch_(lambda: self.cursor.fetchall())

    def __del__(self):
        if self.connected():
            self.disconnect()
