from typing import Callable
from abc import ABC, abstractmethod

from Library.DataFrame import pl
from Library.Logging import HandlerLoggingAPI
from Library.Dataclass import DataclassAPI
from Library.Database import QueryAPI
from Library.Utility import PathAPI, traceback_package
from Library.Statistics import Timer

class DatabaseAPI(ABC):

    _PARAMETER_TOKEN_: Callable[[int], str] = None
    _CHECK_DATATYPE_MAPPING_: dict = None
    _CREATE_DATATYPE_MAPPING_: dict = None
    _DESCRIPTION_DATATYPE_MAPPING_: dict = None
    _STRUCTURE_: dict = None

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if DatabaseAPI not in cls.__bases__: return
        module: str = traceback_package(package=cls.__module__)

        cls.CHECK_DATABASE_QUERY = QueryAPI(PathAPI(path="Check/Database.sql", module=module))
        cls.CHECK_SCHEMA_QUERY = QueryAPI(PathAPI(path="Check/Schema.sql", module=module))
        cls.CHECK_TABLE_QUERY = QueryAPI(PathAPI(path="Check/Table.sql", module=module))
        cls.CHECK_STRUCTURE_QUERY = QueryAPI(PathAPI(path="Check/Structure.sql", module=module))

        cls.CREATE_DATABASE_QUERY = QueryAPI(PathAPI(path="Create/Database.sql", module=module))
        cls.CREATE_SCHEMA_QUERY = QueryAPI(PathAPI(path="Create/Schema.sql", module=module))
        cls.CREATE_TABLE_QUERY = QueryAPI(PathAPI(path="Create/Table.sql", module=module))

        cls.DELETE_DATABASE_QUERY = QueryAPI(PathAPI(path="Delete/Database.sql", module=module))
        cls.DELETE_SCHEMA_QUERY = QueryAPI(PathAPI(path="Delete/Schema.sql", module=module))
        cls.DELETE_TABLE_QUERY = QueryAPI(PathAPI(path="Delete/Table.sql", module=module))

    def __init__(self, *,
                 host: str,
                 port: int,
                 user: str,
                 password: str,
                 admin: bool,
                 database: str,
                 schema: str,
                 table: str,
                 legacy: bool,
                 migrate: bool,
                 autocommit: bool) -> None:

        self._host_: str = host
        self._port_: int = port
        self._user_: str = user
        self._password_: str = password
        self._admin_: bool = admin
        self._legacy_: bool = legacy
        self._migrate_: bool = migrate
        self._autocommit_: bool = autocommit

        self._defaults_: dict = {}
        self.database: str = database
        if self.databased(): self._defaults_["database"] = database
        self.schema: str = schema
        if self.schemed(): self._defaults_["schema"] = schema
        self.table: str = table
        if self.tabled(): self._defaults_["table"] = table

        self._connection_ = None
        self._cursor_ = None

        self._log_ = HandlerLoggingAPI(
            **self._defaults_,
            Class=self.__class__.__name__
        )

    @abstractmethod
    def _check_(self):
        raise NotImplementedError

    @abstractmethod
    def _create_(self):
        raise NotImplementedError

    @abstractmethod
    def _connect_(self, admin: bool):
        raise NotImplementedError

    def connected(self) -> bool:
        return self._connection_ is not None

    def cursored(self) -> bool:
        return self._cursor_ is not None

    def databased(self) -> bool:
        return self.database is not None

    def schemed(self) -> bool:
        return self.schema is not None

    def tabled(self) -> bool:
        return self.table is not None

    def structured(self) -> bool:
        return self._STRUCTURE_ is not None

    def commit(self):
        if self.connected():
            timer = Timer()
            timer.start()
            self._connection_.commit()
            timer.stop()
            self._log_.debug(lambda: f"Commit Operation ({timer.result()})")
        return self

    def rollback(self):
        if self.connected():
            timer = Timer()
            timer.start()
            self._connection_.rollback()
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
            self._connection_ = self._connect_(admin=admin or self._admin_)
            self._cursor_ = self._connection_.cursor()
            timer.stop()
            self._log_.info(lambda: f"Connected to {self._host_}:{self._port_} ({timer.result()})")
            return self
        except Exception as e:
            self._log_.error(lambda: f"Failed at Connect Operation")
            self._log_.exception(lambda: str(e))
            raise e

    def __enter__(self):
        return self.migration() if self._migrate_ else self.connect()

    def disconnect(self):
        try:
            if not self.connected() and not self.cursored():
                return self
            timer = Timer()
            timer.start()
            if self.cursored():
                self._cursor_.close()
                self._cursor_ = None
            if self.connected():
                self._connection_.close()
                self._connection_ = None
            timer.stop()
            self._log_.info(lambda: f"Disconnected from {self._host_}:{self._port_} ({timer.result()})")
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

    def format(self, data, schema: dict = None) -> pl.DataFrame:
        if isinstance(data, pl.DataFrame):
            data = data
        elif isinstance(data, (tuple, list)):
            if any(isinstance(row, DataclassAPI) for row in data):
                data = [row.dict() for row in data]
            else:
                data = data
        elif isinstance(data, DataclassAPI):
            data = [data.dict()]
        else:
            data = None
        return pl.DataFrame(data=data, schema=schema or self._STRUCTURE_, orient="row")

    def _query_(self, query: QueryAPI, *args, **kwargs) -> tuple[str, tuple | None]:
        kwargs = {**self._defaults_, **kwargs}
        return query(self._PARAMETER_TOKEN_, *args, **kwargs)

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
        if not check.is_empty():
            self._log_.debug(lambda: f"Checking Structure: {self.table}")
            definitions = self._check_()
            diff = self.execute(self.CHECK_STRUCTURE_QUERY, definitions=definitions).fetchall()
            self.commit()
            if diff.is_empty(): return
            self._log_.warning(lambda: f"Mismatched Structure: {self.table}")
            self.execute(self.DELETE_TABLE_QUERY)
            self.commit()
            self._log_.info(lambda: f"Deleted Table: {self.table}")
        self._log_.warning(lambda: f"Missing Table: {self.table}")
        definitions = self._create_()
        self.execute(self.CREATE_TABLE_QUERY, definitions=definitions)
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
            if self.tabled() and self.structured():
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
            self._log_.exception(lambda: str(e))
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
            self._log_.exception(lambda: str(e))
            raise e

    def execute(self, query: QueryAPI, *args, **kwargs):
        query, parameters = self._query_(query, *args, **kwargs)
        if parameters is not None: return self._execute_(lambda: self._cursor_.execute(query, parameters))
        else: return self._execute_(lambda: self._cursor_.execute(query))

    def executemany(self, query: QueryAPI, *args, **kwargs):
        if not args:
            e = ValueError("Expecting an Iterable (list or tuple) of Positional Parameters (tuple)")
            self._log_.error("Failed at Executemany Operation")
            self._log_.exception(lambda: str(e))
            raise e
        parameters = args[0]
        query, _ = self._query_(query, **kwargs)
        return self._execute_(lambda: self._cursor_.executemany(query, parameters))

    def _fetch_(self, fetch) -> pl.DataFrame:
        try:
            self.connect()
            timer = Timer()
            timer.start()
            rows = fetch()
            rows = (rows if any(isinstance(row, tuple) for row in rows) else [rows]) if rows else []
            schema = {desc[0]: self._DESCRIPTION_DATATYPE_MAPPING_.get(desc[1]) for desc in self._cursor_.description} if self._cursor_.description else {}
            df = self.format(data=rows, schema=schema)
            timer.stop()
            self._log_.debug(lambda: f"Fetch Operation ({timer.result()}): {len(df)} data points")
            return df.to_pandas() if self._legacy_ else df
        except Exception as e:
            self.rollback()
            self._log_.error(lambda: "Failed at Fetch Operation")
            self._log_.exception(lambda: str(e))
            raise e

    def fetchone(self) -> pl.DataFrame:
        return self._fetch_(lambda: self._cursor_.fetchone())

    def fetchmany(self, n: int) -> pl.DataFrame:
        return self._fetch_(lambda: self._cursor_.fetchmany(n))

    def fetchall(self) -> pl.DataFrame:
        return self._fetch_(lambda: self._cursor_.fetchall())

    def __del__(self):
        self.__exit__(None, None, None)
