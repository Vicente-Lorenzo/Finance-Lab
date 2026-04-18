import pytest

from Library.Database.Query import QueryAPI
from Library.Database.Datapoint import DatapointAPI
from Library.Database.Postgres.Postgres import PostgresDatabaseAPI

@pytest.fixture(scope="session")
def db():
    admin = PostgresDatabaseAPI(admin=True)
    try:
        admin.connect()
        if not admin.exists(database=DatapointAPI.Database):
            admin.create(database=DatapointAPI.Database)
    finally:
        admin.disconnect()

    conn = PostgresDatabaseAPI(database=DatapointAPI.Database)
    try:
        conn.connect()
        conn.executeone(QueryAPI(f'DROP SCHEMA IF EXISTS "{DatapointAPI.Schema}" CASCADE'))
        conn.commit()
        conn.executeone(QueryAPI(f'CREATE SCHEMA "{DatapointAPI.Schema}"'))
        conn.commit()
        yield conn
    finally:
        conn.disconnect()