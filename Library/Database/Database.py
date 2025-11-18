import polars as pl
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_width_chars(-1)
pl.Config.set_fmt_str_lengths(1000)
pl.Config.set_fmt_table_cell_list_len(-1)
from abc import ABC, abstractmethod

from Library.Logging import HandlerAPI
from Library.Dataclass import DataclassAPI
from Library.Database import QueryAPI
from Library.Utility import PathAPI
from Library.Statistics import Timer

class DatabaseAPI(ABC):

    CHECK_DATATYPE_MAPPING = {
        pl.Datetime: "timestamp without time zone",
        pl.Enum: "character varying",
        pl.Int32: "integer",
        pl.Float64: "double precision"
    }

    CREATE_DATATYPE_MAPPING = {
        pl.Datetime: "TIMESTAMP",
        pl.Enum: "VARCHAR",
        pl.Int32: "INTEGER",
        pl.Float64: "DOUBLE PRECISION"
    }

    DESCRIPTION_DATATYPE_MAPPING: dict = None

    CHECK_DATABASE_QUERY = QueryAPI(PathAPI("Check/Database.sql"))
    CHECK_SCHEMA_QUERY = QueryAPI(PathAPI("Check/Schema.sql"))
    CHECK_TABLE_QUERY = QueryAPI(PathAPI("Check/Table.sql"))
    CHECK_STRUCTURE_QUERY = QueryAPI(PathAPI("Check/Structure.sql"))

    CREATE_DATABASE_QUERY = QueryAPI(PathAPI("Create/Database.sql"))
    CREATE_SCHEMA_QUERY = QueryAPI(PathAPI("Create/Schema.sql"))
    CREATE_TABLE_QUERY = QueryAPI(PathAPI("Create/Table.sql"))

    DELETE_DATABASE_QUERY = QueryAPI(PathAPI("Delete/Database.sql"))
    DELETE_SCHEMA_QUERY = QueryAPI(PathAPI("Delete/Schema.sql"))
    DELETE_TABLE_QUERY = QueryAPI(PathAPI("Delete/Table.sql"))

    STRUCTURE: dict = None

    def __init__(self,
                 host: str = None,
                 port: int = None,
                 user: str = None,
                 password: str = None,
                 admin: bool = False,
                 database: str = None,
                 schema: str = None,
                 table: str = None):

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.admin = admin

        self.defaults = {}
        self.database = database
        if self.databased(): self.defaults["database"] = database
        self.schema = schema
        if self.schemed(): self.defaults["schema"] = schema
        self.table = table
        if self.tabled(): self.defaults["table"] = table
        print(self.defaults)

        self.connection = None
        self.cursor = None

        self._log_ = HandlerAPI(
            **self.defaults,
            Class=self.__class__.__name__
        )

    @abstractmethod
    def _connect_(self, admin: bool):
        raise NotImplementedError

    def connected(self) -> bool:
        return self.connection is not None

    def cursored(self) -> bool:
        return self.cursor is not None

    def databased(self) -> bool:
        return self.database is not None

    def schemed(self) -> bool:
        return self.schema is not None

    def tabled(self) -> bool:
        return self.table is not None and self.STRUCTURE is not None

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

    def connect(self, admin: bool = False):
        try:
            if self.connected() and self.cursored():
                return self
            if self.connected() or self.cursored():
                self.disconnect()
            timer = Timer()
            timer.start()
            self.connection = self._connect_(admin=admin or self.admin)
            self.cursor = self.connection.cursor()
            timer.stop()
            self._log_.info(lambda: f"Connected to {self.host}:{self.port} ({timer.result()})")
            return self
        except Exception as e:
            self._log_.error(lambda: f"Failed at Connect Operation")
            self._log_.exception(lambda: str(e))
            raise e

    def __enter__(self):
        self.migration()
        return self

    def disconnect(self):
        try:
            if not self.connected() and not self.cursored():
                return self
            timer = Timer()
            timer.start()
            if self.cursored():
                self.cursor.close()
                self.cursor = None
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
            self.rollback()
            self.disconnect()
            return False
        else:
            self.commit()
            self.disconnect()
            return True

    def format(self, data) -> pl.DataFrame:
        structure = self.STRUCTURE
        if isinstance(data, pl.DataFrame) and data.schema == structure:
            return data
        if isinstance(data, list):
            data = [symbol.dict() for symbol in data]
        elif isinstance(data, DataclassAPI):
            data = [data.dict()]
        else:
            data = None
        return pl.DataFrame(data=data, schema=structure, orient="row")

    def _query_(self, query: QueryAPI, **kwargs) -> str:
        return query(**{**self.defaults, **kwargs})

    def _database_(self):
        self._log_.debug(lambda: f"Checking Database: {self.database}")
        check = self.execute(self.CHECK_DATABASE_QUERY).fetchall()
        self.commit()
        if not check.is_empty(): return
        self._log_.warning(lambda: f"Missing Database: {self.database}")
        self.execute(self.CREATE_DATABASE_QUERY)
        self.commit()
        self._log_.info(lambda: f"Created Database: {self.database}")

    def _schema_(self):
        self._log_.debug(lambda: f"Checking Schema: {self.schema}")
        check = self.execute(self.CHECK_SCHEMA_QUERY).fetchall()
        self.commit()
        if not check.is_empty(): return
        self._log_.warning(lambda: f"Missing Schema: {self.schema}")
        self.execute(self.CREATE_SCHEMA_QUERY)
        self.commit()
        self._log_.info(lambda: f"Created Schema: {self.schema}")

    def _table_(self):
        self._log_.debug(lambda: f"Checking Table: {self.table}")
        check = self.execute(self.CHECK_TABLE_QUERY).fetchall()
        self.commit()
        structure = self.STRUCTURE
        if not check.is_empty():
            self._log_.debug(lambda: f"Checking Structure: {self.table}")
            structure = ", ".join(f"('{name}', '{self.CHECK_DATATYPE_MAPPING[type(dtype)]}')" for name, dtype in structure.items())
            diff = self.execute(self.CHECK_STRUCTURE_QUERY, definitions=structure).fetchall()
            self.commit()
            if diff.is_empty(): return
            self._log_.warning(lambda: f"Mismatched Structure: {self.table}")
            self.execute(self.DELETE_TABLE_QUERY)
            self.commit()
            self._log_.info(lambda: f"Deleted Table: {self.table}")
        self._log_.warning(lambda: f"Missing Table: {self.table}")
        create = ", ".join(f'"{name}" {self.CREATE_DATATYPE_MAPPING[type(dtype)]}' for name, dtype in structure.items())
        self.execute(self.CREATE_TABLE_QUERY, definitions=create)
        self.commit()
        self._log_.info(lambda: f"Created Table: {self.table}")

    def migration(self):
        try:
            timer = Timer()
            timer.start()
            if self.databased():
                subtimer = Timer()
                subtimer.start()
                self.disconnect()
                self.connect(admin=True)
                self._database_()
                subtimer.stop()
                self._log_.info(lambda: f"Database Migration ({subtimer.result()})")
            self.disconnect()
            self.connect()
            if self.schemed():
                subtimer = Timer()
                subtimer.start()
                self._schema_()
                subtimer.stop()
                self._log_.info(lambda: f"Schema Migration ({subtimer.result()})")
            if self.tabled():
                subtimer = Timer()
                subtimer.start()
                self._table_()
                subtimer.stop()
                self._log_.info(lambda: f"Table Migration ({subtimer.result()})")
            timer.stop()
            self._log_.info(lambda: f"Migration Operation ({timer.result()})")
            return self
        except Exception as e:
            self.rollback()
            self._log_.error(lambda: "Failed at Migration Operation")
            raise e

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
            rows = (rows if any(isinstance(row, tuple) for row in rows) else [rows]) if rows else []
            schema = {desc[0]: self.DESCRIPTION_DATATYPE_MAPPING.get(desc[1]) for desc in self.cursor.description} if self.cursor.description else {}
            df = pl.DataFrame(rows, schema=schema, orient="row")
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
        self.__exit__(None, None, None)
