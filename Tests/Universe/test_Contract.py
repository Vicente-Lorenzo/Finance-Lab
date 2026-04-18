from Library.Universe.Ticker import TickerAPI, Contract
from Library.Universe.Provider import ProviderAPI
from Library.Database.Datapoint import DatapointAPI
from Library.Universe.Contract import ContractAPI

def test_contract_initialization(db):
    db.migrate(schema=DatapointAPI.Schema, table=ProviderAPI.Table, structure=ProviderAPI.Structure())
    db.migrate(schema=DatapointAPI.Schema, table=TickerAPI.Table, structure=TickerAPI.Structure())
    try:
        contract = ContractAPI(TickerUID="oanda:eurusd.m", ProviderUID="Pepperstone-Europe", UID=Contract.Spot, db=db)
        assert contract.TickerUID == "EURUSD"
        assert contract.ProviderUID == "Pepperstone-Europe"
        assert contract.UID == Contract.Spot
    except ValueError:
        pass