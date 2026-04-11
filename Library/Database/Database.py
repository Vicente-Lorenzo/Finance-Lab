from typing import Callable
from abc import ABC, abstractmethod
import threading

from Library.Statistics.Timer import Timer
from Library.Dataframe.Dataframe import pd, pl
from Library.Database.Query import QueryAPI
from Library.Service.Service import ServiceAPI
from Library.Logging.Handler import HandlerLoggingAPI
from Library.Utility.Path import PathAPI, traceback_package
from Library.Utility.Typing import MISSING

class DatabaseAPI(ServiceAPI, ABC):

    _ADMIN_: str = None
    _PARAMETER_TOKEN_: Callable[[int], str] = None
    _CHECK_DATATYPE_MAPPING_: dict = None
    _CREATE_DATATYPE_MAPPING_: dict = None
    _DESCRIPTION_DATATYPE_MAPPING_: tuple = None
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
        cls._LIST_CATALOG_QUERY_ = QueryAPI(PathAPI(path="System/List.sql", module=module))
        cls._LIST_SESSIONS_QUERY_ = QueryAPI(PathAPI(path="System/Sessions.sql", module=module))
        cls._KILL_SESSION_QUERY_ = QueryAPI(PathAPI(path="System/Kill.sql", module=module))

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

        self._database_: str = database
        self._schema_: str = schema
        self._table_: str = table

        self._connection_ = None
        self._transaction_ = None
        self._cursor_ = None
        self._pool_ = {}
        self._lock_ = threading.RLock()

        defaults = {k: v for k, v in {"database": database, "schema": schema, "table": table}.items() if v is not None}
        self._log_ = HandlerLoggingAPI(self.__class__.__name__, **defaults)

    @property
    def database(self) -> str | None:
        if self._admin_ or not self._database_: return self._ADMIN_
        return self._database_

    @property
    def schema(self) -> str | None:
        return self._schema_

    @property
    def table(self) -> str | None:
        return self._table_

    @property
    def _hash_(self) -> int:
        params = (
            ("admin", self._admin_),
            ("autocommit", self._autocommit_),
            ("database", self._database_),
            ("host", self._host_),
            ("legacy", self._legacy_),
            ("migrate", self._migrate_),
            ("password", self._password_),
            ("port", self._port_),
            ("schema", self._schema_),
            ("table", self._table_),
            ("user", self._user_)
        )
        return hash(params)

    def clone(self, **kwargs):
        params = {
            "host": self._host_,
            "port": self._port_,
            "user": self._user_,
            "password": self._password_,
            "admin": self._admin_,
            "database": self._database_,
            "schema": self._schema_,
            "table": self._table_,
            "legacy": self._legacy_,
            "migrate": self._migrate_,
            "autocommit": self._autocommit_
        }
        for k, v in kwargs.items():
            if v is not MISSING: params[k] = v
        key = hash(tuple(sorted(params.items())))
        if key == self._hash_:
            self._log_.debug(lambda: "Clone Operation: Skipped (Parameters match self)")
            return self
        with self._lock_:
            if key in self._pool_:
                self._log_.debug(lambda: "Clone Operation: Skipped (Retrieved from pool)")
                return self._pool_[key]
            self._log_.debug(lambda: "Clone Operation: Created (Added to pool)")
            clone = self.__class__(**params)
            self._pool_[key] = clone
            return clone

    @staticmethod
    def _normalize_(dtype):
        if isinstance(dtype, type) and issubclass(dtype, pl.DataType): return dtype
        if isinstance(dtype, pl.DataType): return dtype.__class__
        raise TypeError(f"Not a valid Structure dtype: {dtype}")

    def _concat_(self, frames: list) -> pd.DataFrame | pl.DataFrame:
        if not frames: return self.frame(data=[], schema={})
        if isinstance(frames[0], pl.DataFrame): return pl.concat(frames, how="vertical_relaxed")
        return pd.concat(frames)

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

    def disconnect(self) -> bool:
        with self._lock_:
            for db in self._pool_.values():
                db.disconnect()
            self._pool_.clear()
        return super().disconnect()

    def _disconnect_(self):
        if self._cursor_ is not None:
            self._cursor_.close()
            self._cursor_ = None
        if self._connection_ is not None:
            self._connection_.close()
            self._connection_ = None

    def sessions(self, database: str | object = MISSING) -> pd.DataFrame | pl.DataFrame:
        database = database if database is not MISSING else self.database
        if isinstance(database, (list, tuple)):
            return self._concat_([self.sessions(database=d) for d in database])
        database = database or "%"
        self._log_.debug(lambda: "Sessions Operation: Fetching active sessions")
        return self.execute(self._LIST_SESSIONS_QUERY_, database=database, admin=True).fetchall()

    def kill(self, id: int | str | list | tuple | object = MISSING, database: str | object = MISSING):
        database = database if database is not MISSING else self.database
        if isinstance(database, (list, tuple)):
            for d in database: self.kill(id=id, database=d)
            return self
        with self._lock_:
            for key, clone_db in list(self._pool_.items()):
                if clone_db._database_ == database:
                    clone_db.disconnect()
        if isinstance(id, (list, tuple)):
            for i in id: self.kill(id=i, database=database)
            return self
        if id is MISSING:
            self._log_.debug(lambda: "Kill Operation: Fetching all active sessions to terminate")
            active_sessions = self.sessions(database=database)
            if not active_sessions.is_empty():
                ids = active_sessions["Id"].to_list()
                self.kill(id=ids, database=database)
            return self
        self._log_.alert(lambda: f"Kill Operation: Terminating session {id}")
        try:
            self.execute(self._KILL_SESSION_QUERY_, id=id, admin=True).commit()
        except Exception as e:
            self._log_.error(lambda: f"Kill Operation: Failed to terminate session {id}")
            self._log_.exception(lambda: str(e))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb: self.rollback()
        else: self.commit()
        return super().__exit__(exc_type, exc_val, exc_tb)

    def _query_(self, query: QueryAPI, **kwargs):
        defaults = {}
        if self.database is not None: defaults["database"] = self.database
        if self.schema is not None: defaults["schema"] = self.schema
        if self.table is not None: defaults["table"] = self.table
        kwargs = {**defaults, **kwargs}
        sql, configuration = query.compile(self._PARAMETER_TOKEN_, **kwargs)
        return sql, configuration, kwargs

    def list(self, database: str | object = MISSING, schema: str | object = MISSING, table: str | object = MISSING, system: bool = False) -> pd.DataFrame | pl.DataFrame:
        database = database if database is not MISSING else self._database_
        schema = schema if schema is not MISSING else self._schema_
        table = table if table is not MISSING else self._table_
        if isinstance(database, (list, tuple)):
            return self._concat_([self.list(database=d, schema=schema, table=table, system=system) for d in database])
        if isinstance(schema, (list, tuple)):
            return self._concat_([self.list(database=database, schema=s, table=table, system=system) for s in schema])
        if isinstance(table, (list, tuple)):
            return self._concat_([self.list(database=database, schema=schema, table=t, system=system) for t in table])
        database = database if database and database != "%" else "%"
        schema = schema if schema and schema != "%" else "%"
        table = table if table and table != "%" else "%"
        system = 1 if system else 0
        self._log_.debug(lambda: "List Operation: Fetching structural catalog")
        df = self.execute(self._LIST_CATALOG_QUERY_, database=database, schema=schema, table=table, system=system, admin=True).fetchall()
        if not df.is_empty():
            databases = df["Database"].unique().to_list() if "Database" in df.columns else []
            current_db = self.database
            frames = []
            expansion = False
            if database == "%":
                expansion = True
            else:
                for db_name in databases:
                    if db_name != current_db:
                        expansion = True
                        break
            if expansion:
                for db_name in databases:
                    db = self.execute(self._LIST_CATALOG_QUERY_, database=db_name, schema=schema, table=table, system=system, admin=False)
                    db_df = db.fetchall()
                    if not db_df.is_empty():
                        frames.append(db_df)
                    else:
                        frames.append(df.filter(pl.col("Database") == db_name) if isinstance(df, pl.DataFrame) else df[df["Database"] == db_name])
                if frames:
                    return self._concat_(frames)
        return df

    def exists(self, database: str | object = MISSING, schema: str | object = MISSING, table: str | object = MISSING) -> bool:
        database = database if database is not MISSING else self._database_
        schema = schema if schema is not MISSING else self._schema_
        table = table if table is not MISSING else self._table_
        if isinstance(database, (list, tuple)):
            return all(self.exists(database=d, schema=schema, table=table) for d in database)
        if isinstance(schema, (list, tuple)):
            return all(self.exists(database=database, schema=s, table=table) for s in schema)
        if isinstance(table, (list, tuple)):
            return all(self.exists(database=database, schema=schema, table=t) for t in table)
        if table and (not database or not schema):
            raise ValueError("Schema and Database must be provided to operate on a Table")
        if schema and not database:
            raise ValueError("Database must be provided to operate on a Schema")
        if not database and not schema and not table:
            raise ValueError("At least one structure must be specified")
        kwargs = {k: v for k, v in {"database": database, "schema": schema, "table": table}.items() if v}
        if database:
            self._log_.debug(lambda: f"Check Operation: Checking {database} Database")
            db = self.execute(self._CHECK_DATABASE_QUERY_, **kwargs, admin=True)
            empty = db.fetchall().is_empty()
            if empty: return False
        if schema:
            self._log_.debug(lambda: f"Check Operation: Checking {schema} Schema")
            db = self.execute(self._CHECK_SCHEMA_QUERY_, **kwargs, admin=False)
            empty = db.fetchall().is_empty()
            if empty: return False
        if table:
            self._log_.debug(lambda: f"Check Operation: Checking {table} Table")
            db = self.execute(self._CHECK_TABLE_QUERY_, **kwargs, admin=False)
            empty = db.fetchall().is_empty()
            if empty: return False
        return True

    def diff(self, database: str | object = MISSING, schema: str | object = MISSING, table: str | object = MISSING, structure: dict | object = MISSING) -> bool:
        database = database if database is not MISSING else self._database_
        schema = schema if schema is not MISSING else self._schema_
        table = table if table is not MISSING else self._table_
        structure = structure if structure is not MISSING else self._STRUCTURE_
        if not structure:
            raise ValueError("Structure must be provided to diff a Table")
        if table and (not database or not schema):
            raise ValueError("Schema and Database must be provided to operate on a Table")
        if schema and not database:
            raise ValueError("Database must be provided to operate on a Schema")
        if not database and not schema and not table:
            raise ValueError("At least one structure must be specified")
        kwargs = {k: v for k, v in {"database": database, "schema": schema, "table": table}.items() if v}
        definitions = self._check_(structure=structure)
        self._log_.debug(lambda: f"Diff Operation: Checking {table} Structure")
        db = self.execute(self._CHECK_STRUCTURE_QUERY_, definitions=definitions, **kwargs, admin=False)
        diff_empty = db.fetchall().is_empty()
        return not diff_empty

    def create(self, database: str | object = MISSING, schema: str | object = MISSING, table: str | object = MISSING, structure: dict | object = MISSING):
        database = database if database is not MISSING else self._database_
        schema = schema if schema is not MISSING else self._schema_
        table = table if table is not MISSING else self._table_
        if isinstance(database, (list, tuple)):
            for d in database: self.create(database=d, schema=schema, table=table, structure=structure)
            return self
        if isinstance(schema, (list, tuple)):
            for s in schema: self.create(database=database, schema=s, table=table, structure=structure)
            return self
        if isinstance(table, (list, tuple)):
            for t in table: self.create(database=database, schema=schema, table=t, structure=structure)
            return self
        if table and (not database or not schema):
            raise ValueError("Schema and Database must be provided to operate on a Table")
        if schema and not database:
            raise ValueError("Database must be provided to operate on a Schema")
        if not database and not schema and not table:
            raise ValueError("At least one structure must be specified")
        kwargs = {k: v for k, v in {"database": database, "schema": schema, "table": table}.items() if v}
        if database:
            if not self.exists(database=database, schema=None, table=None):
                self._log_.warning(lambda: f"Create Operation: Missing {database} Database")
                self.execute(self._CREATE_DATABASE_QUERY_, **kwargs, admin=True).commit()
                self._log_.alert(lambda: f"Create Operation: Created {database} Database")
        if schema:
            if not self.exists(database=database, schema=schema, table=None):
                self._log_.warning(lambda: f"Create Operation: Missing {schema} Schema")
                db = self.execute(self._CREATE_SCHEMA_QUERY_, **kwargs, admin=False)
                db.commit()
                self._log_.alert(lambda: f"Create Operation: Created {schema} Schema")
        if table:
            structure_val = structure if structure is not MISSING else self._STRUCTURE_
            if structure_val is None:
                raise ValueError("Structure must be provided to create a Table")
            if not self.exists(database=database, schema=schema, table=table):
                self._log_.warning(lambda: f"Create Operation: Missing {table} Table")
                definitions = self._create_(structure=structure_val)
                db = self.execute(self._CREATE_TABLE_QUERY_, definitions=definitions, **kwargs, admin=False)
                db.commit()
                self._log_.alert(lambda: f"Create Operation: Created {table} Table")
            else:
                if self.diff(database=database, schema=schema, table=table, structure=structure_val):
                    self._log_.warning(lambda: f"Create Operation: Mismatched {table} Structure")
                    db = self.execute(self._DELETE_TABLE_QUERY_, **kwargs, admin=False)
                    db.commit()
                    self._log_.warning(lambda: f"Create Operation: Missing {table} Table")
                    definitions = self._create_(structure=structure_val)
                    db = self.execute(self._CREATE_TABLE_QUERY_, definitions=definitions, **kwargs, admin=False)
                    db.commit()
                    self._log_.alert(lambda: f"Create Operation: Created {table} Table")
        return self

    def delete(self, database: str | object = MISSING, schema: str | object = MISSING, table: str | object = MISSING):
        database = database if database is not MISSING else self._database_
        schema = schema if schema is not MISSING else self._schema_
        table = table if table is not MISSING else self._table_
        if isinstance(database, (list, tuple)):
            for d in database: self.delete(database=d, schema=schema, table=table)
            return self
        if isinstance(schema, (list, tuple)):
            for s in schema: self.delete(database=database, schema=s, table=table)
            return self
        if isinstance(table, (list, tuple)):
            for t in table: self.delete(database=database, schema=schema, table=t)
            return self
        if table and (not database or not schema):
            raise ValueError("Schema and Database must be provided to operate on a Table")
        if schema and not database:
            raise ValueError("Database must be provided to operate on a Schema")
        if not database and not schema and not table:
            raise ValueError("At least one structure must be specified")
        kwargs = {k: v for k, v in {"database": database, "schema": schema, "table": table}.items() if v}
        if table:
            if self.exists(database=database, schema=schema, table=table):
                self.execute(self._DELETE_TABLE_QUERY_, **kwargs, admin=False).commit()
                self._log_.alert(lambda: f"Delete Operation: Deleted {table} Table")
        if schema:
            if self.exists(database=database, schema=schema, table=None):
                self.execute(self._DELETE_SCHEMA_QUERY_, **kwargs, admin=False).commit()
                self._log_.alert(lambda: f"Delete Operation: Deleted {schema} Schema")
        if database:
            if self.exists(database=database, schema=None, table=None):
                self.disconnect()
                self.execute(self._DELETE_DATABASE_QUERY_, **kwargs, admin=True).commit()
                self._log_.alert(lambda: f"Delete Operation: Deleted {database} Database")
        return self

    def migration(self):
        try:
            timer = Timer()
            timer.start()
            if self.databased():
                subtimer = Timer()
                subtimer.start()
                self.disconnect()
                self.connect(admin=True)
                self.create(database=self._database_, schema=None, table=None)
                subtimer.stop()
                self._log_.info(lambda: f"Migration Operation: Migrated Database ({subtimer.result()})")
            self.disconnect()
            self.connect()
            if self.schemed() or self.tabled():
                subtimer = Timer()
                subtimer.start()
                self.create()
                subtimer.stop()
                self._log_.info(lambda: f"Migration Operation: Migrated Schema and Table ({subtimer.result()})")
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
        schema = {}
        for col_name, type_code, *_ in self._cursor_.description or []:
            if self._STRUCTURE_ and col_name in self._STRUCTURE_:
                schema[col_name] = self._STRUCTURE_[col_name]
            elif self._DESCRIPTION_DATATYPE_MAPPING_:
                schema[col_name] = next((p for d, p in self._DESCRIPTION_DATATYPE_MAPPING_ if type_code == d), None)
            else:
                schema[col_name] = None
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

    def execute(self, query: QueryAPI, *args, database: str | object = MISSING, schema: str | object = MISSING, table: str | object = MISSING, admin: bool | object = MISSING, **kwargs):
        if isinstance(database, (list, tuple)):
            for d in database: self.execute(query, *args, database=d, schema=schema, table=table, admin=admin, **kwargs)
            return self
        if isinstance(schema, (list, tuple)):
            for s in schema: self.execute(query, *args, database=database, schema=s, table=table, admin=admin, **kwargs)
            return self
        if isinstance(table, (list, tuple)):
            for t in table: self.execute(query, *args, database=database, schema=schema, table=t, admin=admin, **kwargs)
            return self
        target_db = database if database is not MISSING else self._database_
        target_schema = schema if schema is not MISSING else self._schema_
        target_table = table if table is not MISSING else self._table_
        target_admin = admin if admin is not MISSING else self._admin_
        db = self.clone(database=target_db, schema=target_schema, table=target_table, admin=target_admin)
        if db is not self:
            db.connect()
            return db.execute(query, *args, database=database, schema=schema, table=table, admin=admin, **kwargs)
        if database is not MISSING: kwargs["database"] = database
        if schema is not MISSING: kwargs["schema"] = schema
        if table is not MISSING: kwargs["table"] = table
        sql, configuration, kwargs = self._query_(query, **kwargs)
        parameters = query.bind(configuration, *args, **kwargs) if configuration else None
        def _execute_():
            if parameters is not None: self._cursor_.execute(sql, parameters)
            else: self._cursor_.execute(sql)
            self._transaction_ = True
        timer = self._execute_(callback=_execute_, abort=self.rollback)
        self._log_.info(lambda: f"Execute Operation: Executed ({timer.result()})")
        return self

    def executemany(self, query: QueryAPI, *args, database: str | object = MISSING, schema: str | object = MISSING, table: str | object = MISSING, admin: bool | object = MISSING, **kwargs):
        if isinstance(database, (list, tuple)):
            for d in database: self.executemany(query, *args, database=d, schema=schema, table=table, admin=admin, **kwargs)
            return self
        if isinstance(schema, (list, tuple)):
            for s in schema: self.executemany(query, *args, database=database, schema=s, table=table, admin=admin, **kwargs)
            return self
        if isinstance(table, (list, tuple)):
            for t in table: self.executemany(query, *args, database=database, schema=schema, table=t, admin=admin, **kwargs)
            return self
        target_db = database if database is not MISSING else self._database_
        target_schema = schema if schema is not MISSING else self._schema_
        target_table = table if table is not MISSING else self._table_
        target_admin = admin if admin is not MISSING else self._admin_
        db = self.clone(database=target_db, schema=target_schema, table=target_table, admin=target_admin)
        if db is not self:
            db.connect()
            return db.executemany(query, *args, database=database, schema=schema, table=table, admin=admin, **kwargs)
        if database is not MISSING: kwargs["database"] = database
        if schema is not MISSING: kwargs["schema"] = schema
        if table is not MISSING: kwargs["table"] = table
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
        timer = self._execute_(callback=_execute_, abort=self.rollback)
        self._log_.info(lambda: f"Execute Many Operation: Executed ({timer.result()})")
        return self