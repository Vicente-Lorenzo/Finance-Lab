from Library.Universe.Universe import UniverseAPI
from Library.Universe.Ticker import TickerAPI, Contract
from Library.Universe.Security import SecurityAPI
from Library.Universe.Provider import ProviderAPI
from Library.Universe.Category import CategoryAPI
from Library.Database.Datapoint import DatapointAPI

def test_security_initialization(db):
    db.migrate(schema=UniverseAPI.Schema, table=CategoryAPI.Table, structure=CategoryAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=ProviderAPI.Table, structure=ProviderAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=TickerAPI.Table, structure=TickerAPI.Structure())
    try:
        sec = SecurityAPI(TickerUID="oanda:eurusd.m", ProviderUID="Pepperstone-Europe", ContractUID=Contract.Spot, db=db)
        assert sec.TickerUID == "EURUSD"
        assert sec.ProviderUID == "Pepperstone Europe"
        assert sec.ContractUID == Contract.Spot
    except ValueError:
        pass