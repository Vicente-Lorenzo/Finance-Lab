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
        admin.kill(database="test_database")
        admin.delete(database="test_database")
    except Exception: pass
    finally: admin.disconnect()
    yield PostgresDatabaseAPI
    try:
        admin.connect()
        admin.kill(database="test_database")
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
    api.create(database=("test_db_1", "test_db_2"))
    assert api.exists(database="test_db_1") is True
    assert api.exists(database="test_db_2") is True
    api.create(database="test_db_1", schema=("schema_1", "schema_2"))
    assert api.exists(database="test_db_1", schema=("schema_1", "schema_2")) is True
    api.create(database="test_db_1", schema="schema_1", table="test_table", structure={"id": pl.Int64})
    api.create(database="test_db_1", schema="schema_2", table="test_table", structure={"id": pl.Int64})
    df_all = api.list()
    databases = df_all["Database"].to_list()
    assert "test_db_1" in databases
    assert "test_db_2" in databases
    assert "postgres" not in databases
    schemas = df_all["Schema"].to_list()
    assert "schema_1" in schemas
    assert "schema_2" in schemas
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
    df_many = api.execute(select).fetchmany(n=2)
    assert len(df_many) == 2
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    assert cleaner.exists(database="test_database") is False

def test_structure_mismatch(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database")
    api.create(schema="test_schema")
    api.create(schema="test_schema", table="test_table", structure={"id": pl.Int64})
    api.create(schema="test_schema", table="test_table", structure={"id": pl.Int64, "name": pl.String})
    df = api.executeone(QueryAPI("SELECT * FROM test_schema.test_table LIMIT 0")).fetchall()
    assert "name" in df.columns
    api.disconnect()
    admin.disconnect()

def test_refactor_database(db):
    api = db(admin=True)
    api.create(database="test_database")
    api.refactor(database="test_database", name="test_database_renamed")
    assert api.exists(database="test_database") is False
    assert api.exists(database="test_database_renamed") is True
    api.disconnect()
    cleaner = db(admin=True)
    cleaner.delete(database="test_database_renamed")
    cleaner.disconnect()

def test_refactor_schema(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database")
    api.create(schema="old_schema")
    api.refactor(schema="old_schema", name="new_schema")
    assert api.exists(schema="new_schema") is True
    assert api.exists(schema="old_schema") is False
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_refactor_table(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    setup = db(database="test_database")
    setup.create(schema="test_schema")
    setup.create(schema="test_schema", table="old_table", structure={"id": pl.Int64, "name": pl.String})
    setup.executeone(QueryAPI("INSERT INTO test_schema.old_table (id, name) VALUES (:id:, :name:)"), id=1, name="A")
    setup.disconnect()
    api = db(database="test_database", schema="test_schema")
    api.refactor(table="old_table", name="new_table")
    assert api.exists(table="new_table") is True
    assert api.exists(table="old_table") is False
    df = api.executeone(QueryAPI("SELECT * FROM test_schema.new_table")).fetchall()
    assert len(df) == 1
    assert df["name"][0] == "A"
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_refactor_lowest_level_default(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    setup = db(database="test_database")
    setup.create(schema="test_schema")
    setup.create(schema="test_schema", table="t1", structure={"id": pl.Int64})
    setup.disconnect()
    api = db(database="test_database", schema="test_schema", table="t1")
    api.refactor(name="t2")
    assert api.exists(database="test_database", schema="test_schema", table="t2") is True
    assert api.exists(database="test_database", schema="test_schema", table="t1") is False
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_refactor_iterable_databases(db):
    api = db(admin=True)
    api.create(database=("refactor_a", "refactor_b"))
    api.refactor(database=("refactor_a", "refactor_b"), name=("refactor_x", "refactor_y"))
    assert api.exists(database=("refactor_x", "refactor_y")) is True
    assert api.exists(database="refactor_a") is False
    assert api.exists(database="refactor_b") is False
    api.disconnect()
    cleaner = db(admin=True)
    cleaner.delete(database=("refactor_x", "refactor_y"))
    cleaner.disconnect()

def test_refactor_iterable_tables(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    setup = db(database="test_database")
    setup.create(schema="test_schema")
    setup.create(schema="test_schema", table=("t1", "t2"), structure={"id": pl.Int64})
    setup.disconnect()
    api = db(database="test_database", schema="test_schema")
    api.refactor(table=("t1", "t2"), name=("t1_new", "t2_new"))
    assert api.exists(table=("t1_new", "t2_new")) is True
    assert api.exists(table="t1") is False
    assert api.exists(table="t2") is False
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_refactor_validation(db):
    api = db(admin=True)
    with pytest.raises(ValueError): api.refactor(database="x")
    with pytest.raises(ValueError): api.refactor(name="x")
    with pytest.raises(ValueError): api.refactor(schema="s", name="x")
    with pytest.raises(ValueError): api.refactor(table="t", name="x")
    with pytest.raises(ValueError): api.refactor(database="nonexistent_db", name="other")
    with pytest.raises(ValueError): api.refactor(database=("a", "b"), name="single")
    with pytest.raises(ValueError): api.refactor(database=("a", "b"), name=("only_one",))
    api.disconnect()

def test_rename_column(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    setup = db(database="test_database")
    setup.create(schema="test_schema")
    setup.create(schema="test_schema", table="test_table", structure={"old_id": pl.Int64, "old_name": pl.String, "value": pl.Float64})
    setup.executeone(QueryAPI("INSERT INTO test_schema.test_table (old_id, old_name, value) VALUES (:id:, :name:, :v:)"), id=1, name="A", v=1.5)
    setup.disconnect()
    api = db(database="test_database", schema="test_schema", table="test_table")
    api.rename(column="old_id", name="new_id")
    df = api.executeone(QueryAPI("SELECT * FROM test_schema.test_table")).fetchall()
    assert "new_id" in df.columns
    assert "old_id" not in df.columns
    assert df["new_id"][0] == 1
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_rename_iterable_columns(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    setup = db(database="test_database")
    setup.create(schema="test_schema")
    setup.create(schema="test_schema", table="test_table", structure={"a": pl.Int64, "b": pl.String, "c": pl.Float64})
    setup.disconnect()
    api = db(database="test_database", schema="test_schema", table="test_table")
    api.rename(column=("a", "b", "c"), name=("alpha", "beta", "gamma"))
    df = api.executeone(QueryAPI("SELECT * FROM test_schema.test_table LIMIT 0")).fetchall()
    assert "alpha" in df.columns
    assert "beta" in df.columns
    assert "gamma" in df.columns
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_rename_validation(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    setup = db(database="test_database")
    setup.create(schema="test_schema")
    setup.create(schema="test_schema", table="test_table", structure={"id": pl.Int64})
    setup.disconnect()
    api = db(database="test_database", schema="test_schema", table="test_table")
    with pytest.raises(ValueError): api.rename(column="id")
    with pytest.raises(ValueError): api.rename(name="id")
    with pytest.raises(ValueError): api.rename(column=("a", "b"), name="single")
    api2 = db(admin=True)
    with pytest.raises(ValueError): api2.rename(column="a", name="b")
    api3 = db(database="test_database", schema="test_schema", table="nonexistent_table")
    with pytest.raises(ValueError): api3.rename(column="a", name="b")
    api.disconnect()
    api2.disconnect()
    api3.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_crud_operations(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database", schema="test_schema", table="test_table")
    api.create(structure={"id": pl.Int64, "name": pl.String, "value": pl.Float64})
    data = [{"id": 1, "name": "A", "value": 10.0}, {"id": 2, "name": "B", "value": 20.0}]
    api.insert(data=data)
    df = api.select()
    assert len(df) == 2
    assert "A" in df["name"].to_list()
    df = api.select(condition="id = 1", limit=1)
    assert len(df) == 1
    assert df["value"][0] == 10.0
    api.update(data=[{"id": 2, "value": 25.0}], condition="id = :id:")
    df = api.select(condition="id = 2")
    assert df["value"][0] == 25.0
    api.remove(condition="id = 1")
    df = api.select()
    assert len(df) == 1
    assert df["id"][0] == 2
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_schema_operations(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database", schema="test_schema", table="test_table")
    api.create(structure={"id": pl.Int64})
    api.add(structure={"name": pl.String, "value": pl.Float64})
    api.insert(data=[{"id": 1, "name": "A", "value": 10.0}])
    df = api.select()
    assert "name" in df.columns
    assert "value" in df.columns
    assert len(df) == 1
    api.drop(column="value")
    df = api.select()
    assert "value" not in df.columns
    assert "name" in df.columns
    api.add(structure={"value": pl.Float64})
    api.update(data={"value": 20.0}, condition="id = 1")
    api.reorder(columns=["name", "value", "id"])
    df = api.select()
    assert list(df.columns) == ["name", "value", "id"]
    assert df["value"][0] == 20.0
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_crud_positional_operations(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database", schema="test_schema", table="test_table")
    api.create(structure={"id": pl.Int64, "name": pl.String, "value": pl.Float64})
    api.insert(data=(1, "A", 10.0))
    df = api.select()
    assert len(df) == 1
    assert df["name"][0] == "A"
    api.insert(data=[2, "B", 20.0])
    df = api.select()
    assert len(df) == 2
    assert "B" in df["name"].to_list()
    api.insert(data=[(3, "C", 30.0), (4, "D", 40.0)])
    df = api.select()
    assert len(df) == 4
    api.update(data={"value": 25.0}, condition="id = 2")
    df = api.select(condition="id = 2")
    assert df["value"][0] == 25.0
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_upsert_operations(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database", schema="test_schema", table="test_table")
    api.create(structure={"id": pl.Int64, "name": pl.String, "value": pl.Float64})
    api.executeone(QueryAPI("ALTER TABLE test_schema.test_table ADD PRIMARY KEY (id)"))
    api.insert(data=[{"id": 1, "name": "A", "value": 10.0}, {"id": 2, "name": "B", "value": 20.0}])
    api.upsert(data=[{"id": 2, "name": "B", "value": 25.0}, {"id": 3, "name": "C", "value": 30.0}], key="id")
    df = api.select(order="id")
    assert len(df) == 3
    assert df["value"].to_list() == [10.0, 25.0, 30.0]
    api.upsert(data={"id": 1, "name": "A", "value": 15.0}, key="id")
    df = api.select(condition="id = 1")
    assert df["value"][0] == 15.0
    api.upsert(data=[{"id": 4, "name": "D", "value": 40.0}], key="id")
    df = api.select(order="id")
    assert len(df) == 4
    assert df["name"].to_list() == ["A", "B", "C", "D"]
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_dataframe_input(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database", schema="test_schema", table="test_table")
    api.create(structure={"id": pl.Int64, "name": pl.String, "value": pl.Float64})
    df_input = pl.DataFrame({"id": [1, 2], "name": ["A", "B"], "value": [10.0, 20.0]})
    api.insert(data=df_input)
    df = api.select(order="id")
    assert len(df) == 2
    assert df["name"].to_list() == ["A", "B"]
    df_update = pl.DataFrame({"id": [1], "value": [15.0]})
    api.update(data=df_update, condition="id = :id:")
    df = api.select(condition="id = 1")
    assert df["value"][0] == 15.0
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()

def test_select_columns(db):
    admin = db(admin=True)
    admin.create(database="test_database")
    api = db(database="test_database", schema="test_schema", table="test_table")
    api.create(structure={"id": pl.Int64, "name": pl.String, "value": pl.Float64})
    api.insert(data=[{"id": 1, "name": "A", "value": 10.0}])
    df = api.select(columns=["id", "name"])
    assert list(df.columns) == ["id", "name"]
    assert "value" not in df.columns
    df = api.select(order="id", limit=1)
    assert len(df) == 1
    api.disconnect()
    admin.disconnect()
    cleaner = db(admin=True)
    cleaner.kill(database="test_database")
    cleaner.delete(database="test_database")
    cleaner.disconnect()
