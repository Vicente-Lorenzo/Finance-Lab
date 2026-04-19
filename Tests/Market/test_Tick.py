import pytest
from datetime import datetime
from Library.Market.Tick import TickAPI, TickMode
from Library.Universe.Security import SecurityAPI
from Library.Universe.Category import CategoryAPI
from Library.Universe.Provider import ProviderAPI, Platform
from Library.Universe.Ticker import TickerAPI, Contract
from Library.Universe.Universe import UniverseAPI

def test_tick_initialization(db):
    db.migrate(schema=UniverseAPI.Schema, table=CategoryAPI.Table, structure=CategoryAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=ProviderAPI.Table, structure=ProviderAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=TickerAPI.Table, structure=TickerAPI.Structure())

    CategoryAPI(UID="Forex (Major)", Primary="Forex", Secondary="Major", Alternative="Currency", db=db).push(by="test")
    ProviderAPI(UID="Pepperstone (cTrader)", Platform=Platform.cTrader, Name="Pepperstone Europe", Abbreviation="Pepperstone", db=db).push(by="test")
    TickerAPI(UID="EURUSD", Category="Forex (Major)", BaseAsset="EUR", BaseName="Euro", QuoteAsset="USD", QuoteName="US Dollar", Description="Euro vs US Dollar", db=db).push(by="test")

    sec = SecurityAPI(TickerUID="EURUSD", ProviderUID="Pepperstone (cTrader)", ContractUID=Contract.Spot, db=db)
    sec.push(by="test")
    dt = datetime(2023, 1, 1, 12, 0, 0)
    tick = TickAPI(SecurityUID=sec.UID, timestamp=dt, ask=1.0500, bid=1.0498, Volume=100.0, contract=sec.Contract, db=db)
    
    assert tick.SecurityUID == sec.UID
    assert tick.DateTime == dt
    assert tick.AskPrice == pytest.approx(1.0500)
    assert tick.BidPrice == 1.0498
    assert tick.Volume == 100.0
    assert tick.MidPrice == 1.0499

    from Library.Database.Query import QueryAPI
    db.executeone(QueryAPI(f'DELETE FROM "{TickAPI.Schema}"."{TickAPI.Table}"')).commit()