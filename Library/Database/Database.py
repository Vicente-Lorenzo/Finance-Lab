from typing import Callable
from abc import ABC, abstractmethod

from Library.API.API import API
from Library.Statistics import Timer
from Library.Database import QueryAPI
from Library.Logging import HandlerLoggingAPI
from Library.Dataframe import pd, pl, DataframeAPI
from Library.Utility import PathAPI, traceback_package

class DatabaseAPI(API, DataframeAPI, ABC):

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
        super().__init__(legacy=legacy)

        self._host_: str = host
        self._port_: int = port
        self._user_: str = user
        self._password_: str = password
        self._admin_: bool = admin
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

        self._log_ = HandlerLoggingAPI(self.__class__.__name__, **self._defaults_)

    @staticmethod
    def _normalize_(dtype):
        if isinstance(dtype, type) and issubclass(dtype, pl.DataType):
            return dtype
        if isinstance(dtype, pl.DataType):
            return dtype.__class__
        raise TypeError(f"Not a valid Structure dtype: {dtype}")

    @abstractmethod
    def _check_(self):
        raise NotImplementedError

    @abstractmethod
    def _create_(self):
        raise NotImplementedError

    @abstractmethod
    def _driver_(self, admin: bool):
        raise NotImplementedError

    def connected(self) -> bool:
        return self._connection_ is not None and self._cursor_ is not None

    def disconnected(self) -> bool:
        return self._connection_ is None and self._cursor_ is None

    def autocommited(self) -> bool:
        return self._autocommit_ is True

    def transitioned(self) -> bool:
        return self._transaction_ is True

    def databased(self) -> bool:
        return self.database is not None

    def schemed(self) -> bool:
        return self.schema is not None

    def tabled(self) -> bool:
        return self.table is not None

    def structured(self) -> bool:
        return self._STRUCTURE_ is not None

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

    def _connect_(self, admin: bool = False):
        self._connection_ = self._driver_(admin=admin or self._admin_)
        self._transaction_ = False
        self._cursor_ = self._connection_.cursor()

    def __enter__(self):
        return self.migration() if self._migrate_ else self.connect()

    def _disconnect_(self):
        if self._cursor_ is not None:
            self._cursor_.close()
            self._cursor_ = None
        if self._connection_ is not None:
            self._connection_.close()
            self._connection_ = None

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type or exception_value or exception_traceback:
            self.rollback()
        else:
            self.commit()
        return super().__exit__(exception_type, exception_value, exception_traceback)

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
        timer = self._execute_(lambda: self._cursor_.executemany(sql, parameters))
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
            df = self.frame(data=rows, schema=schema or self._STRUCTURE_)
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
