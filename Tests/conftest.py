import pytest

from Library.Database.Query import QueryAPI
from Library.Database.Datapoint import DatapointAPI
from Library.Database.Postgres.Postgres import PostgresDatabaseAPI
from Library.Universe.Universe import UniverseAPI
from Library.Market.Market import MarketAPI
from Library.Portfolio.Portfolio import PortfolioAPI

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
        conn.executeone(QueryAPI(f'DROP SCHEMA IF EXISTS "{UniverseAPI.Schema}" CASCADE'))
        conn.executeone(QueryAPI(f'DROP SCHEMA IF EXISTS "{MarketAPI.Schema}" CASCADE'))
        conn.executeone(QueryAPI(f'DROP SCHEMA IF EXISTS "{PortfolioAPI.Schema}" CASCADE'))
        conn.commit()
        conn.executeone(QueryAPI(f'CREATE SCHEMA "{UniverseAPI.Schema}"'))
        conn.executeone(QueryAPI(f'CREATE SCHEMA "{MarketAPI.Schema}"'))
        conn.executeone(QueryAPI(f'CREATE SCHEMA "{PortfolioAPI.Schema}"'))
        conn.commit()
        yield conn
    finally:
        conn.disconnect()