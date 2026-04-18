from Library.Universe.Ticker import TickerAPI
from Library.Universe.Contract import Instrument
from Library.Universe.Security import SecurityAPI
from Library.Universe.Provider import ProviderAPI
from Library.Universe.Category import CategoryAPI
from Library.Database.Datapoint import DatapointAPI

def test_security_initialization(db):
    db.migrate(schema=DatapointAPI.Schema, table=CategoryAPI.Table, structure=CategoryAPI.Structure())
    db.migrate(schema=DatapointAPI.Schema, table=ProviderAPI.Table, structure=ProviderAPI.Structure())
    db.migrate(schema=DatapointAPI.Schema, table=TickerAPI.Table, structure=TickerAPI.Structure())
    try:
        sec = SecurityAPI(TickerUID="oanda:eurusd.m", ProviderUID="Pepperstone-Europe", Instrument=Instrument.Spot, db=db)
        assert sec.TickerUID == "EURUSD"
        assert sec.ProviderUID == "Pepperstone Europe"
        assert sec.Instrument == Instrument.Spot
    except ValueError:
        pass