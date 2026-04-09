from typing import Callable
from abc import ABC, abstractmethod

from Library.Statistics import Timer
from Library.Dataframe import pd, pl
from Library.Database import QueryAPI
from Library.Service import ServiceAPI
from Library.Logging import HandlerLoggingAPI
from Library.Utility import PathAPI, traceback_package

class DatabaseAPI(ServiceAPI, ABC):

    _PARAMETER_TOKEN_: Callable[[int], str] = None
    _CHECK_DATATYPE_MAPPING_: dict = None
    _CREATE_DATATYPE_MAPPING_: dict = None
    _DESCRIPTION_DATATYPE_MAPPING_: dict = None
    _STRUCTURE_: dict = None

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if DatabaseAPI not in cls.__bases__: return
        module: str = traceback_package(package=cls.__module__)
        cls._CHECK_DATABASE_QUERY_ = QueryAPI(PathAPI(path="Database/Check.sql", module=module))
        cls._CREATE_DATABASE_QUERY_ = QueryAPI(PathAPI(path="Database/Create.sql", module=module))
        cls._DELETE_DATABASE_QUERY_ = QueryAPI(PathAPI(path="Database/Delete.sql", module=module))
        cls._CHECK_SCHEMA_QUERY_ = QueryAPI(PathAPI(path="Schema/Check.sql", module=module))
        cls._CREATE_SCHEMA_QUERY_ = QueryAPI(PathAPI(path="Schema/Create.sql", module=module))
        cls._DELETE_SCHEMA_QUERY_ = QueryAPI(PathAPI(path="Schema/Delete.sql", module=module))
        cls._CHECK_TABLE_QUERY_ = QueryAPI(PathAPI(path="Table/Check.sql", module=module))
        cls._CREATE_TABLE_QUERY_ = QueryAPI(PathAPI(path="Table/Create.sql", module=module))
        cls._DELETE_TABLE_QUERY_ = QueryAPI(PathAPI(path="Table/Delete.sql", module=module))
        cls._CHECK_STRUCTURE_QUERY_ = QueryAPI(PathAPI(path="Table/Structure.sql", module=module))
        cls._LIST_CATALOG_QUERY_ = QueryAPI(PathAPI(path="Catalog/List.sql", module=module))

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
        if isinstance(dtype, type) and issubclass(dtype, pl.DataType): return dtype
        if isinstance(dtype, pl.DataType): return dtype.__class__
        raise TypeError(f"Not a valid Structure dtype: {dtype}")

    @abstractmethod
    def _check_(self, structure: dict = None): raise NotImplementedError

    @abstractmethod
    def _create_(self, structure: dict = None): raise NotImplementedError

    @abstractmethod
    def _driver_(self, admin: bool): raise NotImplementedError

    def connected(self) -> bool: return self._connection_ is not None and self._cursor_ is not None

    def disconnected(self) -> bool: return self._connection_ is None and self._cursor_ is None

    def autocommited(self) -> bool: return self._autocommit_ is True

    def transitioned(self) -> bool: return self._transaction_ is True

    def databased(self) -> bool: return self.database is not None

    def schemed(self) -> bool: return self.schema is not None

    def tabled(self) -> bool: return self.table is not None

    def structured(self) -> bool: return self._STRUCTURE_ is not None

    def commit(self):
        if not self.connected(): self._log_.debug(lambda: "Commit Operation: Skipped (Not Connected)")
        elif self.autocommited(): self._log_.debug(lambda: "Commit Operation: Skipped (Autocommit Enabled)")
        elif not self.transitioned(): self._log_.debug(lambda: "Commit Operation: Skipped (No Open Transaction)")
        else:
            timer = Timer()
            timer.start()
            self._connection_.commit()
            self._transaction_ = False
            timer.stop()
            self._log_.info(lambda: f"Commit Operation: Closed Transaction ({timer.result()})")
        return self

    def rollback(self):
        if not self.connected(): self._log_.debug(lambda: "Rollback Operation: Skipped (Not Connected)")
        elif self.autocommited(): self._log_.debug(lambda: "Rollback Operation: Skipped (Autocommit Enabled)")
        elif not self.transitioned(): self._log_.debug(lambda: "Rollback Operation: Skipped (No Open Transaction)")
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

    def __enter__(self): return self.migration() if self._migrate_ else self.connect()

    def _disconnect_(self):
        if self._cursor_ is not None:
            self._cursor_.close()
            self._cursor_ = None
        if self._connection_ is not None:
            self._connection_.close()
            self._connection_ = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb: self.rollback()
        else: self.commit()
        return super().__exit__(exc_type, exc_val, exc_tb)

    def _query_(self, query: QueryAPI, **kwargs):
        kwargs = {**self._defaults_, **kwargs}
        sql, configuration = query.compile(self._PARAMETER_TOKEN_, **kwargs)
        return sql, configuration, kwargs

    def list(self, database: str = None, schema: str = None, table: str = None, system: bool = False) -> pd.DataFrame | pl.DataFrame:
        database = database or self.database or "%"
        schema = schema or self.schema or "%"
        table = table or self.table or "%"
        system = 1 if system else 0
        self._log_.debug(lambda: "List Operation: Fetching structural catalog")
        return self.execute(self._LIST_CATALOG_QUERY_, database=database, schema=schema, table=table, system=system).fetchall()

    def exists(self, database: str = None, schema: str = None, table: str = None) -> bool:
        database = database or self.database
        schema = schema or self.schema
        table = table or self.table
        if table is not None and (database is None or schema is None):
            raise ValueError("Schema and Database must be provided to operate on a Table")
        if schema is not None and database is None:
            raise ValueError("Database must be provided to operate on a Schema")
        if database is None and schema is None and table is None:
            raise ValueError("At least one structure must be specified")
        kwargs = {k: v for k, v in {"database": database, "schema": schema, "table": table}.items() if v is not None}
        result = True
        if database is not None:
            self._log_.debug(lambda: f"Check Operation: Checking {database} Database")
            if self.execute(self._CHECK_DATABASE_QUERY_, **kwargs).fetchall().is_empty():
                result = False
        if schema is not None:
            self._log_.debug(lambda: f"Check Operation: Checking {schema} Schema")
            if self.execute(self._CHECK_SCHEMA_QUERY_, **kwargs).fetchall().is_empty():
                result = False
        if table is not None:
            self._log_.debug(lambda: f"Check Operation: Checking {table} Table")
            if self.execute(self._CHECK_TABLE_QUERY_, **kwargs).fetchall().is_empty():
                result = False
        return result

    def create(self, database: str = None, schema: str = None, table: str = None, structure: dict = None):
        database = database or self.database
        schema = schema or self.schema
        table = table or self.table
        if table is not None and (database is None or schema is None):
            raise ValueError("Schema and Database must be provided to operate on a Table")
        if schema is not None and database is None:
            raise ValueError("Database must be provided to operate on a Schema")
        if database is None and schema is None and table is None:
            raise ValueError("At least one structure must be specified")
        kwargs = {k: v for k, v in {"database": database, "schema": schema, "table": table}.items() if v is not None}
        if database is not None:
            if not self.exists(database=database):
                self._log_.warning(lambda: f"Create Operation: Missing {database} Database")
                self.execute(self._CREATE_DATABASE_QUERY_, **kwargs)
                self.commit()
                self._log_.alert(lambda: f"Create Operation: Created {database} Database")
        if schema is not None:
            if not self.exists(database=database, schema=schema):
                self._log_.warning(lambda: f"Create Operation: Missing {schema} Schema")
                self.execute(self._CREATE_SCHEMA_QUERY_, **kwargs)
                self.commit()
                self._log_.alert(lambda: f"Create Operation: Created {schema} Schema")
        if table is not None:
            structure = structure if structure is not None else self._STRUCTURE_
            if structure is None:
                raise ValueError("Structure must be provided to create a Table")
            if not self.exists(database=database, schema=schema, table=table):
                self._log_.warning(lambda: f"Create Operation: Missing {table} Table")
                definitions = self._create_(structure=structure)
                self.execute(self._CREATE_TABLE_QUERY_, definitions=definitions, **kwargs)
                self.commit()
                self._log_.alert(lambda: f"Create Operation: Created {table} Table")
            else:
                self._log_.debug(lambda: f"Create Operation: Checking {table} Structure")
                definitions = self._check_(structure=structure)
                diff = self.execute(self._CHECK_STRUCTURE_QUERY_, definitions=definitions, **kwargs).fetchall()
                if not diff.is_empty():
                    self._log_.warning(lambda: f"Create Operation: Mismatched {table} Structure")
                    self.execute(self._DELETE_TABLE_QUERY_, **kwargs)
                    self.commit()
                    self._log_.alert(lambda: f"Create Operation: Deleted {table} Table")
                    self._log_.warning(lambda: f"Create Operation: Missing {table} Table")
                    definitions = self._create_(structure=structure)
                    self.execute(self._CREATE_TABLE_QUERY_, definitions=definitions, **kwargs)
                    self.commit()
                    self._log_.alert(lambda: f"Create Operation: Created {table} Table")

    def delete(self, database: str = None, schema: str = None, table: str = None):
        database = database or self.database
        schema = schema or self.schema
        table = table or self.table
        if table is not None and (database is None or schema is None):
            raise ValueError("Schema and Database must be provided to operate on a Table")
        if schema is not None and database is None:
            raise ValueError("Database must be provided to operate on a Schema")
        if database is None and schema is None and table is None:
            raise ValueError("At least one structure must be specified")
        kwargs = {k: v for k, v in {"database": database, "schema": schema, "table": table}.items() if v is not None}
        if table is not None:
            if self.exists(database=database, schema=schema, table=table):
                self.execute(self._DELETE_TABLE_QUERY_, **kwargs)
                self.commit()
                self._log_.alert(lambda: f"Delete Operation: Deleted {table} Table")
        if schema is not None:
            if self.exists(database=database, schema=schema):
                self.execute(self._DELETE_SCHEMA_QUERY_, **kwargs)
                self.commit()
                self._log_.alert(lambda: f"Delete Operation: Deleted {schema} Schema")
        if database is not None:
            if self.exists(database=database):
                self.execute(self._DELETE_DATABASE_QUERY_, **kwargs)
                self.commit()
                self._log_.alert(lambda: f"Delete Operation: Deleted {database} Database")

    def migration(self):
        try:
            timer = Timer()
            timer.start()
            if self.databased():
                subtimer = Timer()
                subtimer.start()
                self.disconnect()
                self.connect(admin=True)
                self.create(database=self.database)
                subtimer.stop()
                self._log_.info(lambda: f"Migration Operation: Migrated Database ({subtimer.result()})")
            self.disconnect()
            self.connect()
            if self.schemed():
                subtimer = Timer()
                subtimer.start()
                self.create(schema=self.schema)
                subtimer.stop()
                self._log_.info(lambda: f"Migration Operation: Migrated Schema ({subtimer.result()})")
            if self.tabled() and self.structured():
                subtimer = Timer()
                subtimer.start()
                self.create(table=self.table)
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

    def _frame_(self, result):
        if result is None: rows = []
        elif isinstance(result, list): rows = result
        elif isinstance(result, tuple): rows = [result]
        else: rows = list(result)
        schema = self._STRUCTURE_.copy() if self._STRUCTURE_ else {}
        for col_name, type_code, *_ in self._cursor_.description or []:
            if self._STRUCTURE_ and col_name in self._STRUCTURE_:
                schema[col_name] = self._STRUCTURE_[col_name]
            elif self._DESCRIPTION_DATATYPE_MAPPING_:
                schema[col_name] = next((p for d, p in self._DESCRIPTION_DATATYPE_MAPPING_ if type_code == d), None)
        return self.frame(data=rows, schema=schema)

    def fetchone(self) -> pd.DataFrame | pl.DataFrame:
        timer, df = self._fetch_(callback=lambda: self._frame_(self._cursor_.fetchone()), abort=self.rollback)
        self._log_.info(lambda: f"Fetch One Operation: Fetched {len(df)} data points ({timer.result()})")
        return df

    def fetchmany(self, n: int) -> pd.DataFrame | pl.DataFrame:
        timer, df = self._fetch_(callback=lambda: self._frame_(self._cursor_.fetchmany(n)), abort=self.rollback)
        self._log_.info(lambda: f"Fetch Many Operation: Fetched {len(df)} data points ({timer.result()})")
        return df

    def fetchall(self) -> pd.DataFrame | pl.DataFrame:
        timer, df = self._fetch_(callback=lambda: self._frame_(self._cursor_.fetchall()), abort=self.rollback)
        self._log_.info(lambda: f"Fetch All Operation: Fetched {len(df)} data points ({timer.result()})")
        return df

    def execute(self, query: QueryAPI, *args, **kwargs):
        sql, configuration, kwargs = self._query_(query, **kwargs)
        parameters = query.bind(configuration, *args, **kwargs) if configuration else None
        def _execute_():
            if parameters is not None: self._cursor_.execute(sql, parameters)
            else: self._cursor_.execute(sql)
            self._transaction_ = True
        timer = super()._execute_(callback=_execute_, abort=self.rollback)
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
        def _execute_():
            self._cursor_.executemany(sql, parameters)
            self._transaction_ = True
        timer = super()._execute_(callback=_execute_, abort=self.rollback)
        self._log_.info(lambda: f"Execute Many Operation: Executed ({timer.result()})")
        return self