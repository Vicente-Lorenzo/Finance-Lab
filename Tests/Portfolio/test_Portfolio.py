import pytest
from datetime import datetime
from Library.Portfolio.Account import AccountAPI, AccountType, MarginMode, Environment
from Library.Portfolio.Position import PositionAPI, PositionType, TradeType
from Library.Portfolio.Trade import TradeAPI
from Library.Universe.Security import SecurityAPI
from Library.Universe.Category import CategoryAPI
from Library.Universe.Provider import ProviderAPI, Platform
from Library.Universe.Ticker import TickerAPI, Contract
from Library.Universe.Universe import UniverseAPI

def test_portfolio_initialization(db):
    db.migrate(schema=UniverseAPI.Schema, table=CategoryAPI.Table, structure=CategoryAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=ProviderAPI.Table, structure=ProviderAPI.Structure())
    db.migrate(schema=UniverseAPI.Schema, table=TickerAPI.Table, structure=TickerAPI.Structure())

    CategoryAPI(UID="Forex (Major)", Primary="Forex", Secondary="Major", Alternative="Currency", db=db).push(by="test")
    provider = ProviderAPI(UID="Pepperstone (cTrader)", Platform=Platform.cTrader, Name="Pepperstone Europe", Abbreviation="Pepperstone", db=db)
    provider.push(by="test")
    TickerAPI(UID="EURUSD", Category="Forex (Major)", BaseAsset="EUR", BaseName="Euro", QuoteAsset="USD", QuoteName="US Dollar", Description="Euro vs US Dollar", db=db).push(by="test")

    acc = AccountAPI(
        UID="123456",
        ProviderUID=provider.UID,
        Environment=Environment.Live,
        AccountType=AccountType.Hedged,
        MarginMode=MarginMode.Net,
        Asset="USD",
        Balance=10000.0,
        Equity=10050.0,
        Credit=0.0,
        Leverage=30.0,
        MarginUsed=500.0,
        MarginFree=9550.0,
        MarginLevel=2010.0,
        MarginStopLevel=50.0,
        db=db
    )
    assert acc.UID == "123456"
    assert acc.ProviderUID == "Pepperstone (cTrader)"
    assert acc.Environment == Environment.Live
    assert acc.AccountType == AccountType.Hedged

    sec = SecurityAPI(TickerUID="EURUSD", ProviderUID="Pepperstone (cTrader)", ContractUID=Contract.Spot, db=db)
    sec.push(by="test")
    dt = datetime(2023, 1, 1, 12, 0, 0)
    
    pos = PositionAPI(
        PositionID=1001,
        SecurityUID=sec.UID,
        PositionType=PositionType.Normal,
        TradeType=TradeType.Buy,
        Volume=100000,
        Quantity=1.0,
        EntryTimestamp=dt,
        EntryPrice=1.0500,
        StopLossPrice=1.0450,
        TakeProfitPrice=1.0600,
        UsedMargin=500.0,
        EntryBalance=10000.0,
        contract=sec.Contract,
        db=db
    )
    assert pos.PositionID == 1001
    assert pos.SecurityUID == sec.UID
    assert pos.TradeType == TradeType.Buy
    assert pos.EntryPrice == pytest.approx(1.0500)

    exit_dt = datetime(2023, 1, 1, 14, 0, 0)
    trade = TradeAPI(
        TradeID=2001,
        SecurityUID=sec.UID,
        PositionType=PositionType.Normal,
        TradeType=TradeType.Buy,
        Volume=100000,
        Quantity=1.0,
        EntryTimestamp=dt,
        EntryPrice=1.0500,
        ExitTimestamp=exit_dt,
        ExitPrice=1.0550,
        GrossPnL=500.0,
        NetPnL=495.0,
        CommissionPnL=-5.0,
        EntryBalance=10000.0,
        ExitBalance=10495.0,
        contract=sec.Contract,
        db=db
    )
    assert trade.TradeID == 2001
    assert trade.ExitPrice == pytest.approx(1.0550)
    assert trade.NetPnL == pytest.approx(495.0)

    from Library.Database.Query import QueryAPI
    db.executeone(QueryAPI(f'DELETE FROM "{TradeAPI.Schema}"."{TradeAPI.Table}"')).commit()
    db.executeone(QueryAPI(f'DELETE FROM "{PositionAPI.Schema}"."{PositionAPI.Table}"')).commit()
    db.executeone(QueryAPI(f'DELETE FROM "{AccountAPI.Schema}"."{AccountAPI.Table}"')).commit()