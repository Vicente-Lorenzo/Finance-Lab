import pytest
from datetime import datetime

from Library.Dataframe import pl
from Library.Database import QueryAPI
from Library.Database.Postgres import PostgresDatabaseAPI

@pytest.fixture
def db():
    admin = PostgresDatabaseAPI(admin=True)
    try:
        admin.connect()
        admin.delete(database="test_database")
    except Exception: pass
    finally: admin.disconnect()
    yield PostgresDatabaseAPI
    try:
        admin.connect()
        admin.delete(database="test_database")
    except Exception: pass
    finally: admin.disconnect()

def test_exists_only(db):
    api = db(admin=True)
    assert api.exists(database="postgres") is True
    assert api.exists(database="non_existent_db") is False

def test_create_only(db):
    api = db(admin=True)
    api.create(database="test_database")
    assert api.exists(database="test_database") is True

def test_delete_only(db):
    api = db(admin=True)
    api.create(database="test_database")
    api.delete(database="test_database")
    assert api.exists(database="test_database") is False

def test_list_only(db):
    api = db(admin=True)
    api.create(database="test_database")
    df = api.list(database="test_database")
    assert not df.is_empty()
    assert "test_database" in df["Database"].to_list()

def test_iterable_structures(db):
    api = db(admin=True)
    # create multiple databases using a tuple
    api.create(database=("test_db_1", "test_db_2"))
    assert api.exists(database="test_db_1") is True
    assert api.exists(database="test_db_2") is True
    
    # create multiple schemas in a specific database
    api.create(database="test_db_1", schema=("schema_1", "schema_2"))
    assert api.exists(database="test_db_1", schema=("schema_1", "schema_2")) is True

    # create a table in schema_1 so the schema appears in Postgres information_schema.tables
    api.create(database="test_db_1", schema="schema_1", table="test_table", structure={"id": pl.Int64})
    api.create(database="test_db_1", schema="schema_2", table="test_table", structure={"id": pl.Int64})

    # test cross-database global list
    df_all = api.list()
    databases = df_all["Database"].to_list()
    assert "test_db_1" in databases
    assert "test_db_2" in databases
    assert "postgres" not in databases # default system=False omits postgres
    
    # check schemas from cross-database list
    schemas = df_all["Schema"].to_list()
    assert "schema_1" in schemas
    assert "schema_2" in schemas
    
    # cleanup using tuples
    api.disconnect()
    api.delete(database=("test_db_1", "test_db_2"))
    assert api.exists(database=("test_db_1", "test_db_2")) is False

def test_migration(db):
    api = db(database="test_database", schema="test_schema", table="test_table", migrate=True)
    api._STRUCTURE_ = {"id": pl.Int64, "value": pl.String}
    with api:
        assert api.exists(database="test_database", schema="test_schema", table="test_table") is True
    api.disconnect()

def test_mixed_operations(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database")
    api.create(schema="test_schema")
    structure = {"id": pl.Int64, "name": pl.String, "value": pl.Float64, "ts": pl.Datetime}
    api.create(schema="test_schema", table="test_table", structure=structure)
    assert api.exists(schema="test_schema", table="test_table") is True
    query = QueryAPI("INSERT INTO test_schema.test_table (id, name, value, ts) VALUES (:id:, :name:, :value:, :ts:)")
    data = [
        {"id": 1, "name": "A", "value": 1.1, "ts": datetime(2026, 1, 1)},
        {"id": 2, "name": "B", "value": 2.2, "ts": datetime(2026, 1, 2)}
    ]
    api.executemany(query, data)
    select = QueryAPI("SELECT * FROM test_schema.test_table ORDER BY id")
    df_all = api.execute(select).fetchall()
    assert len(df_all) == 2
    assert df_all["id"].to_list() == [1, 2]
    df_one = api.execute(select).fetchone()
    assert len(df_one) == 1
    assert df_one["id"][0] == 1
    df_many = api.execute(select).fetchmany(2)
    assert len(df_many) == 2
    
    api.disconnect()
    admin.disconnect()
    
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database", schema="test_schema", table="test_table")
    assert cleaner.exists(database="test_database") is False

def test_structure_mismatch(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database")
    api.create(schema="test_schema")
    api.create(schema="test_schema", table="test_table", structure={"id": pl.Int64})
    api.create(schema="test_schema", table="test_table", structure={"id": pl.Int64, "name": pl.String})
    df = api.execute(QueryAPI("SELECT * FROM test_schema.test_table LIMIT 0")).fetchall()
    assert "name" in df.columns
    
    api.disconnect()
    admin.disconnect()
