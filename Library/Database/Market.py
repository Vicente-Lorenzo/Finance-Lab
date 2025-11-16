import polars as pl

from Library.Dataclass import *
from Library.Database import PostgresAPI, QueryAPI
from Library.Utility import PathAPI

class MarketDatabaseAPI(PostgresAPI):

    CHECK_DATATYPE = {
        pl.Datetime: "timestamp without time zone",
        pl.Enum: "character varying",
        pl.Int32: "integer",
        pl.Float64: "double precision"
    }

    CREATE_DATATYPE = {
        pl.Datetime: "TIMESTAMP",
        pl.Enum: "VARCHAR",
        pl.Int32: "INTEGER",
        pl.Float64: "DOUBLE PRECISION"
    }

    SYMBOL_SCHEMA: dict = {
        SymbolAPI.ID.BaseAssetType: pl.Enum([currency.name for currency in AssetType]),
        SymbolAPI.ID.QuoteAssetType: pl.Enum([currency.name for currency in AssetType]),
        SymbolAPI.ID.Digits: pl.Int32(),
        SymbolAPI.ID.PointSize: pl.Float64(),
        SymbolAPI.ID.PipSize: pl.Float64(),
        SymbolAPI.ID.LotSize: pl.Int32(),
        SymbolAPI.ID.VolumeMin: pl.Float64(),
        SymbolAPI.ID.VolumeMax: pl.Float64(),
        SymbolAPI.ID.VolumeStep: pl.Float64(),
        SymbolAPI.ID.Commission: pl.Float64(),
        SymbolAPI.ID.CommissionMode: pl.Enum([commission.name for commission in CommissionMode]),
        SymbolAPI.ID.SwapLong: pl.Float64(),
        SymbolAPI.ID.SwapShort: pl.Float64(),
        SymbolAPI.ID.SwapMode: pl.Enum([swap.name for swap in SwapMode]),
        SymbolAPI.ID.SwapExtraDay: pl.Enum([day.name for day in DayOfWeek]),
        SymbolAPI.ID.SwapSummerTime: pl.Int32(),
        SymbolAPI.ID.SwapWinterTime: pl.Int32(),
        SymbolAPI.ID.SwapPeriod: pl.Int32()
    }

    TICK_SCHEMA: dict = {
        TickAPI.ID.Timestamp.DateTime: pl.Datetime(),
        TickAPI.ID.Ask.Price: pl.Float64(),
        TickAPI.ID.Bid.Price: pl.Float64(),
        TickAPI.ID.AskBaseConversion: pl.Float64(),
        TickAPI.ID.BidBaseConversion: pl.Float64(),
        TickAPI.ID.AskQuoteConversion: pl.Float64(),
        TickAPI.ID.BidQuoteConversion: pl.Float64()
    }

    BAR_SCHEMA: dict = {
        BarAPI.ID.Timestamp.DateTime: pl.Datetime(),

        BarAPI.ID.GapTick.Timestamp.DateTime: pl.Datetime(),
        BarAPI.ID.GapTick.Ask.Price: pl.Float64(),
        BarAPI.ID.GapTick.Bid.Price: pl.Float64(),
        BarAPI.ID.GapTick.AskBaseConversion: pl.Float64(),
        BarAPI.ID.GapTick.BidBaseConversion: pl.Float64(),
        BarAPI.ID.GapTick.AskQuoteConversion: pl.Float64(),
        BarAPI.ID.GapTick.BidQuoteConversion: pl.Float64(),

        BarAPI.ID.OpenTick.Timestamp.DateTime: pl.Datetime(),
        BarAPI.ID.OpenTick.Ask.Price: pl.Float64(),
        BarAPI.ID.OpenTick.Bid.Price: pl.Float64(),
        BarAPI.ID.OpenTick.AskBaseConversion: pl.Float64(),
        BarAPI.ID.OpenTick.BidBaseConversion: pl.Float64(),
        BarAPI.ID.OpenTick.AskQuoteConversion: pl.Float64(),
        BarAPI.ID.OpenTick.BidQuoteConversion: pl.Float64(),

        BarAPI.ID.HighTick.Timestamp.DateTime: pl.Datetime(),
        BarAPI.ID.HighTick.Ask.Price: pl.Float64(),
        BarAPI.ID.HighTick.Bid.Price: pl.Float64(),
        BarAPI.ID.HighTick.AskBaseConversion: pl.Float64(),
        BarAPI.ID.HighTick.BidBaseConversion: pl.Float64(),
        BarAPI.ID.HighTick.AskQuoteConversion: pl.Float64(),
        BarAPI.ID.HighTick.BidQuoteConversion: pl.Float64(),

        BarAPI.ID.LowTick.Timestamp.DateTime: pl.Datetime(),
        BarAPI.ID.LowTick.Ask.Price: pl.Float64(),
        BarAPI.ID.LowTick.Bid.Price: pl.Float64(),
        BarAPI.ID.LowTick.AskBaseConversion: pl.Float64(),
        BarAPI.ID.LowTick.BidBaseConversion: pl.Float64(),
        BarAPI.ID.LowTick.AskQuoteConversion: pl.Float64(),
        BarAPI.ID.LowTick.BidQuoteConversion: pl.Float64(),

        BarAPI.ID.CloseTick.Timestamp.DateTime: pl.Datetime(),
        BarAPI.ID.CloseTick.Ask.Price: pl.Float64(),
        BarAPI.ID.CloseTick.Bid.Price: pl.Float64(),
        BarAPI.ID.CloseTick.AskBaseConversion: pl.Float64(),
        BarAPI.ID.CloseTick.BidBaseConversion: pl.Float64(),
        BarAPI.ID.CloseTick.AskQuoteConversion: pl.Float64(),
        BarAPI.ID.CloseTick.BidQuoteConversion: pl.Float64(),

        BarAPI.ID.TickVolume: pl.Float64()
    }

    TRADE_SCHEMA: dict = {
        TradeAPI.ID.PositionID: pl.Int32(),
        TradeAPI.ID.TradeID: pl.Int32(),
        TradeAPI.ID.PositionType: pl.Enum([position.name for position in PositionType]),
        TradeAPI.ID.TradeType: pl.Enum([trade.name for trade in TradeType]),

        TradeAPI.ID.Volume: pl.Float64(),
        TradeAPI.ID.Quantity: pl.Float64(),

        TradeAPI.ID.EntryTimestamp.DateTime: pl.Datetime(),
        TradeAPI.ID.ExitTimestamp.DateTime: pl.Datetime(),
        TradeAPI.ID.EntryPrice.Price: pl.Float64(),
        TradeAPI.ID.StopLossPrice.Price: pl.Float64(),
        TradeAPI.ID.TakeProfitPrice.Price: pl.Float64(),
        TradeAPI.ID.MaxRunUpPrice.Price: pl.Float64(),
        TradeAPI.ID.MaxDrawDownPrice.Price: pl.Float64(),
        TradeAPI.ID.ExitPrice.Price: pl.Float64(),

        TradeAPI.ID.StopLossPnL.PnL: pl.Float64(),
        TradeAPI.ID.TakeProfitPnL.PnL: pl.Float64(),
        TradeAPI.ID.MaxRunUpPnL.PnL: pl.Float64(),
        TradeAPI.ID.MaxDrawDownPnL.PnL: pl.Float64(),
        TradeAPI.ID.GrossPnL.PnL: pl.Float64(),
        TradeAPI.ID.CommissionPnL.PnL: pl.Float64(),
        TradeAPI.ID.SwapPnL.PnL: pl.Float64(),
        TradeAPI.ID.NetPnL.PnL: pl.Float64(),

        TradeAPI.ID.EntryBalance: pl.Float64(),
        TradeAPI.ID.MidBalance: pl.Float64(),
        TradeAPI.ID.ExitBalance: pl.Float64(),
    }

    CHECK_DATABASE_QUERY = QueryAPI(PathAPI("Check/Database.sql"))
    CHECK_SCHEMA_QUERY = QueryAPI(PathAPI("Check/Schema.sql"))
    CHECK_TABLE_QUERY = QueryAPI(PathAPI("Check/Table.sql"))

    CREATE_DATABASE_QUERY = QueryAPI(PathAPI("Create/Database.sql"))
    CREATE_SCHEMA_QUERY = QueryAPI(PathAPI("Create/Schema.sql"))
    CREATE_TABLE_QUERY = QueryAPI(PathAPI("Create/Table.sql"))

    DELETE_DATABASE_QUERY = QueryAPI(PathAPI("Delete/Database.sql"))
    DELETE_SCHEMA_QUERY = QueryAPI(PathAPI("Delete/Schema.sql"))
    DELETE_TABLE_QUERY = QueryAPI(PathAPI("Delete/Table.sql"))

    STRUCTURE_TABLE_QUERY = QueryAPI(PathAPI("Structure/Table.sql"))

    def __init__(self,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str):

        super().__init__(
            database=broker,
            schema=symbol,
            table=timeframe
        )

        self.broker = broker
        self.group = group
        self.symbol = symbol
        self.timeframe = timeframe

    def _database_(self):
        self.execute(self.CHECK_DATABASE_QUERY)
        check = self.fetchall()
        self.commit()
        if not check.is_empty(): return
        self.execute(self.CREATE_DATABASE_QUERY)
        self.commit()
        self._log_.info(lambda: f"Created {self.database} database")

    def _schema_(self):
        self.execute(self.CHECK_SCHEMA_QUERY)
        check = self.fetchall()
        self.commit()
        if not check.is_empty(): return
        self.execute(self.CREATE_SCHEMA_QUERY)
        self.commit()
        self._log_.info(lambda: f"Created {self.schema} schema")

    def _table_(self):
        self.execute(self.CHECK_TABLE_QUERY)
        check = self.fetchall()
        self.commit()
        if not result.is_empty(): return
        self.execute(self.CREATE_TABLE_QUERY)
        self.commit()

    @staticmethod
    def format_data(data, schema: dict) -> pl.DataFrame:
        if isinstance(data, pl.DataFrame) and data.schema == schema:
            return data
        if isinstance(data, list):
            data = [symbol.dict() for symbol in data]
        elif isinstance(data, SymbolAPI):
            data = [data.dict()]
        else:
            data = None
        return pl.DataFrame(data=data, schema=schema, orient="row")

    @classmethod
    def format_symbol_data(cls, data: pl.DataFrame | list[SymbolAPI] | SymbolAPI | None) -> pl.DataFrame:
        return cls.format_data(data=data, schema=cls.SYMBOL_SCHEMA)

    @classmethod
    def format_tick_data(cls, data: pl.DataFrame | list[TickAPI] | TickAPI | None) -> pl.DataFrame:
        return cls.format_data(data=data, schema=cls.TICK_SCHEMA)

    @classmethod
    def format_bar_data(cls, data: pl.DataFrame | list[BarAPI] | BarAPI | None) -> pl.DataFrame:
        return cls.format_data(data=data, schema=cls.BAR_SCHEMA)

    @classmethod
    def format_trade_data(cls, data: pl.DataFrame | list[TradeAPI] | TradeAPI | None) -> pl.DataFrame:
        return cls.format_data(data=data, schema=cls.TRADE_SCHEMA)
