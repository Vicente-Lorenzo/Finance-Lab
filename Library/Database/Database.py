import atexit
from typing import Callable
from abc import ABC, abstractmethod

from Library.DataFrame import pd, pl
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

        cls._CHECK_DATABASE_QUERY_ = QueryAPI(PathAPI(path="Check/Database.sql", module=module))
        cls._CHECK_SCHEMA_QUERY_ = QueryAPI(PathAPI(path="Check/Schema.sql", module=module))
        cls._CHECK_TABLE_QUERY_ = QueryAPI(PathAPI(path="Check/Table.sql", module=module))
        cls._CHECK_STRUCTURE_QUERY_ = QueryAPI(PathAPI(path="Check/Structure.sql", module=module))

        cls._CREATE_DATABASE_QUERY_ = QueryAPI(PathAPI(path="Create/Database.sql", module=module))
        cls._CREATE_SCHEMA_QUERY_ = QueryAPI(PathAPI(path="Create/Schema.sql", module=module))
        cls._CREATE_TABLE_QUERY_ = QueryAPI(PathAPI(path="Create/Table.sql", module=module))

        cls._DELETE_DATABASE_QUERY_ = QueryAPI(PathAPI(path="Delete/Database.sql", module=module))
        cls._DELETE_SCHEMA_QUERY_ = QueryAPI(PathAPI(path="Delete/Schema.sql", module=module))
        cls._DELETE_TABLE_QUERY_ = QueryAPI(PathAPI(path="Delete/Table.sql", module=module))

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
        self._transaction_ = None
        self._cursor_ = None
        self._guard_ = None

        self._log_ = HandlerLoggingAPI(self.__class__.__name__, **self._defaults_)

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

    def autocommited(self) -> bool:
        return self._autocommit_ is True

    def transitioned(self) -> bool:
        return self._transaction_ is True

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

    def guarded(self) -> bool:
        return self._guard_ is not None

    def commit(self):
        if not self.connected():
            self._log_.debug(lambda: "Commit Operation: Skipped (Not Connected)")
        elif self.autocommited():
            self._log_.debug(lambda: "Commit Operation: Skipped (Autocommit Enabled)")
        elif not self.transitioned():
            self._log_.debug(lambda: "Commit Operation: Skipped (No Open Transaction)")
        else:
            timer = Timer()
            timer.start()
            self._connection_.commit()
            self._transaction_ = False
            timer.stop()
            self._log_.info(lambda: f"Commit Operation: Closed Transaction ({timer.result()})")
        return self

    def rollback(self):
        if not self.connected():
            self._log_.debug(lambda: "Rollback Operation: Skipped (Not Connected)")
        elif self.autocommited():
            self._log_.debug(lambda: "Rollback Operation: Skipped (Autocommit Enabled)")
        elif not self.transitioned():
            self._log_.debug(lambda: "Rollback Operation: Skipped (No Open Transaction)")
        else:
            timer = Timer()
            timer.start()
            self._connection_.rollback()
            self._transaction_ = False
            timer.stop()
            self._log_.info(lambda: f"Rollback Operation: Closed Transaction ({timer.result()})")
        return self

    def connect(self, admin: bool = False):
        try:
            if self.connected() and self.cursored():
                self._log_.debug(lambda: "Connect Operation: Skipped (Already Connected)")
                return self
            if self.connected() or self.cursored():
                self._log_.warning(lambda: "Connect Operation: Disconnecting (Bad Connection)")
                self.disconnect()
            timer = Timer()
            timer.start()
            self._connection_ = self._connect_(admin=admin or self._admin_)
            self._transaction_ = False
            self._cursor_ = self._connection_.cursor()
            if not self.guarded():
                self._guard_ = self.disconnect
                try: atexit.register(self._guard_)
                except: pass
            timer.stop()
            self._log_.info(lambda: f"Connect Operation: Connected ({timer.result()})")
            return self
        except Exception as e:
            self._log_.error(lambda: f"Connect Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise

    def __enter__(self):
        return self.migration() if self._migrate_ else self.connect()

    def disconnect(self):
        try:
            if not self.connected() and not self.cursored():
                self._log_.debug(lambda: "Disconnect Operation: Skipped (Not Connected)")
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
            if self.guarded():
                try: atexit.unregister(self._guard_)
                except: pass
                self._guard_ = None
            self._log_.info(lambda: f"Disconnect Operation: Disconnected ({timer.result()})")
            return self
        except Exception as e:
            self._log_.error(lambda: f"Disconnect Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise

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

    def flatten(self, data) -> list:
        if isinstance(data, pd.DataFrame):
            return data.to_dicts(orient="records")
        if isinstance(data, pd.Series):
            return data.to_list()
        if isinstance(data, pl.DataFrame):
            return data.to_dicts()
        if isinstance(data, pl.Series):
            return data.to_list()
        if isinstance(data, DataclassAPI):
            return [data.dict()]
        if not isinstance(data, (tuple, list, set)):
            return [data] if data else []
        if all(isinstance(item, (list, tuple, set)) for item in data):
            return list(data)
        flat = []
        for item in data:
            flat.extend(self.flatten(item))
        return flat

    def format(self, data, schema: dict = None) -> pd.DataFrame | pl.DataFrame:
        data: list = self.flatten(data)
        schema: dict = schema if schema else self._STRUCTURE_
        df: pl.DataFrame = pl.DataFrame(data=data, schema=schema, orient="row", strict=False)
        return df.to_pandas() if self._legacy_ else df

    def _query_(self, query: QueryAPI, **kwargs):
        kwargs = {**self._defaults_, **kwargs}
        sql, configuration = query.compile(self._PARAMETER_TOKEN_, **kwargs)
        return sql, configuration, kwargs

    def _database_(self):
        self._log_.debug(lambda: f"Migration Operation: Checking {self.database} Database")
        check = self.execute(self._CHECK_DATABASE_QUERY_).fetchall()
        if not check.is_empty(): return
        self._log_.warning(lambda: f"Migration Operation: Missing {self.database} Database")
        self.execute(self._CREATE_DATABASE_QUERY_)
        self.commit()
        self._log_.alert(lambda: f"Migration Operation: Created {self.database} Database")

    def _schema_(self):
        self._log_.debug(lambda: f"Migration Operation: Checking {self.schema} Schema")
        check = self.execute(self._CHECK_SCHEMA_QUERY_).fetchall()
        if not check.is_empty(): return
        self._log_.warning(lambda: f"Migration Operation: Missing {self.schema} Schema")
        self.execute(self._CREATE_SCHEMA_QUERY_)
        self.commit()
        self._log_.alert(lambda: f"Migration Operation: Created {self.schema} Schema")

    def _table_(self):
        self._log_.debug(lambda: f"Migration Operation: Checking {self.table} Table")
        check = self.execute(self._CHECK_TABLE_QUERY_).fetchall()
        if not check.is_empty():
            self._log_.debug(lambda: f"Migration Operation: Checking {self.table} Structure")
            definitions = self._check_()
            diff = self.execute(self._CHECK_STRUCTURE_QUERY_, definitions=definitions).fetchall()
            if diff.is_empty(): return
            self._log_.warning(lambda: f"Migration Operation: Mismatched {self.table} Structure")
            self.execute(self._DELETE_TABLE_QUERY_)
            self.commit()
            self._log_.alert(lambda: f"Migration Operation: Deleted {self.table} Table")
        self._log_.warning(lambda: f"Migration Operation: Missing {self.table} Table")
        definitions = self._create_()
        self.execute(self._CREATE_TABLE_QUERY_, definitions=definitions)
        self.commit()
        self._log_.alert(lambda: f"Migration Operation: Created {self.table} Table")

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
                self._log_.info(lambda: f"Migration Operation: Migrated Database ({subtimer.result()})")
            self.disconnect()
            self.connect()
            if self.schemed():
                subtimer = Timer()
                subtimer.start()
                self._schema_()
                subtimer.stop()
                self._log_.info(lambda: f"Migration Operation: Migrated Schema ({subtimer.result()})")
            if self.tabled() and self.structured():
                subtimer = Timer()
                subtimer.start()
                self._table_()
                subtimer.stop()
                self._log_.info(lambda: f"Migration Operation: Migrated Table ({subtimer.result()})")
            timer.stop()
            self._log_.info(lambda: f"Migration Operation: Migrated ({timer.result()})")
            return self
        except Exception as e:
            self.rollback()
            self._log_.error(lambda: "Migration Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise

    def _execute_(self, execute):
        try:
            self.connect()
            timer = Timer()
            timer.start()
            execute()
            self._transaction_ = True
            timer.stop()
            return timer
        except Exception as e:
            self.rollback()
            self._log_.error(lambda: "Execute Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise

    def execute(self, query: QueryAPI, *args, **kwargs):
        sql, configuration, kwargs = self._query_(query, **kwargs)
        parameters = query.bind(configuration, *args, **kwargs) if configuration else None
        if parameters is not None: timer = self._execute_(lambda: self._cursor_.execute(sql, parameters))
        else: timer = self._execute_(lambda: self._cursor_.execute(sql))
        self._log_.info(lambda: f"Execute Operation: Executed ({timer.result()})")
        return self

    def executemany(self, query: QueryAPI, *args, **kwargs):
        batch = self.flatten(args[0]) if len(args) == 1 else self.flatten(args)
        if not batch or not all(isinstance(row, (list, tuple, dict)) for row in batch):
            e = ValueError("Expecting batch as tuple/list of tuples/lists or tuple/list of dicts")
            self._log_.error(lambda: "Execute Many Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise e
        if not all(isinstance(row, type(batch[0])) for row in batch):
            e = ValueError("Expecting batch to be the same type (all tuples, all lists, or all dicts)")
            self._log_.error(lambda: "Execute Many Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise e
        sql, configuration, kwargs = self._query_(query, **kwargs)
        parameters = []
        for row in batch:
            if isinstance(row, dict): parameters.append(query.bind(configuration, **{**kwargs, **row}))
            else: parameters.append(query.bind(configuration, *row, **kwargs))
        timer = self._execute_(lambda: self._cursor_.execute(sql, parameters))
        self._log_.info(lambda: f"Execute Many Operation: Executed ({timer.result()})")
        return self

    def _fetch_(self, fetch):
        try:
            self.connect()
            timer = Timer()
            timer.start()
            result = fetch()
            if result is None:
                rows = []
            elif isinstance(result, list):
                rows = result
            elif isinstance(result, tuple):
                rows = [result]
            else:
                rows = list(result)
            schema = {
                desc[0]: self._DESCRIPTION_DATATYPE_MAPPING_.get(desc[1])
                for desc in self._cursor_.description
            } if self._cursor_.description else {}
            df = self.format(data=rows, schema=schema)
            timer.stop()
            return timer, df
        except Exception as e:
            self.rollback()
            self._log_.error(lambda: "Failed at Fetch Operation")
            self._log_.exception(lambda: str(e))
            raise

    def fetchone(self) -> pd.DataFrame | pl.DataFrame:
        timer, df = self._fetch_(lambda: self._cursor_.fetchone())
        self._log_.info(lambda: f"Fetch One Operation: Fetched {len(df)} data points ({timer.result()})")
        return df

    def fetchmany(self, n: int) -> pd.DataFrame | pl.DataFrame:
        timer, df = self._fetch_(lambda: self._cursor_.fetchmany(n))
        self._log_.info(lambda: f"Fetch Many Operation: Fetched {len(df)} data points ({timer.result()})")
        return df

    def fetchall(self) -> pd.DataFrame | pl.DataFrame:
        timer, df =  self._fetch_(lambda: self._cursor_.fetchall())
        self._log_.info(lambda: f"Fetch All Operation: Fetched {len(df)} data points ({timer.result()})")
        return df

    def __del__(self):
        try: self.disconnect()
        except: pass
