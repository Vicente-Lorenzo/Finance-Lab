import pytest
from Library.Universe.Contract import ContractAPI
from Library.Universe.Ticker import TickerAPI
from Library.Universe.Provider import ProviderAPI
from Library.Database.Datapoint import DatapointAPI

def test_contract_initialization(db):
    db.migrate(schema=DatapointAPI.Schema, table=ProviderAPI.Table, structure=ProviderAPI.Structure())
    db.migrate(schema=DatapointAPI.Schema, table=TickerAPI.Table, structure=TickerAPI.Structure())
    try:
        contract = ContractAPI(TickerUID="oanda:eurusd.m", ProviderUID="Pepperstone-Europe", db=db)
        assert contract.TickerUID == "EURUSD"
        assert contract.ProviderUID == "Pepperstone Europe"
    except ValueError:
        pass