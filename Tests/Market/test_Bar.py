import pytest
from datetime import datetime
from Library.Market.Bar import BarAPI
from Library.Universe.Security import SecurityAPI
from Library.Universe.Timeframe import TimeframeAPI
from Library.Universe.Category import CategoryAPI
from Library.Universe.Provider import ProviderAPI, Platform
from Library.Universe.Ticker import TickerAPI, Contract
from Library.Universe.Universe import UniverseAPI

def test_bar_initialization(db):
    db.migrate(schema=UniverseAPI.Schema, table=CategoryAPI.Table, structure=CategoryAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=ProviderAPI.Table, structure=ProviderAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=TickerAPI.Table, structure=TickerAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=TimeframeAPI.Table, structure=TimeframeAPI.Structure())

    CategoryAPI(UID="Forex (Major)", Primary="Forex", Secondary="Major", Alternative="Currency", db=db).push(by="test")
    ProviderAPI(UID="Pepperstone (cTrader)", Platform=Platform.cTrader, Name="Pepperstone Europe", Abbreviation="Pepperstone", db=db).push(by="test")
    TickerAPI(UID="EURUSD", Category="Forex (Major)", BaseAsset="EUR", BaseName="Euro", QuoteAsset="USD", QuoteName="US Dollar", Description="Euro vs US Dollar", db=db).push(by="test")
    tf = TimeframeAPI(UID="M1", db=db)
    tf.push(by="test")

    sec = SecurityAPI(TickerUID="EURUSD", ProviderUID="Pepperstone (cTrader)", ContractUID=Contract.Spot, db=db)
    sec.push(by="test")
    dt = datetime(2023, 1, 1, 12, 0, 0)
    
    bar = BarAPI(
        SecurityUID=sec.UID, 
        TimeframeUID=tf.UID,
        timestamp=dt, 
        OpenAskPrice=1.0500, OpenBidPrice=1.0498,
        HighAskPrice=1.0510, HighBidPrice=1.0508,
        LowAskPrice=1.0490, LowBidPrice=1.0488,
        CloseAskPrice=1.0505, CloseBidPrice=1.0503,
        TickVolume=150.0, 
        contract=sec.Contract, 
        db=db
    )
    
    assert bar.SecurityUID == sec.UID
    assert bar.TimeframeUID == tf.UID
    assert bar.DateTime == dt
    assert bar.OpenAskPrice == pytest.approx(1.0500)
    assert bar.HighAskPrice == pytest.approx(1.0510)
    assert bar.LowAskPrice == pytest.approx(1.0490)
    assert bar.CloseAskPrice == pytest.approx(1.0505)
    
    assert bar.MidOpen == pytest.approx(1.0499)
    assert bar.MidHigh == pytest.approx(1.0509)
    assert bar.MidLow == pytest.approx(1.0489)
    assert bar.MidClose == pytest.approx(1.0504)
    
    assert bar.RangeHighLow == pytest.approx(0.0020)
    assert bar.RangeOpenClose == pytest.approx(0.0005)

    from Library.Database.Query import QueryAPI
    db.executeone(QueryAPI(f'DELETE FROM "{BarAPI.Schema}"."{BarAPI.Table}"')).commit()