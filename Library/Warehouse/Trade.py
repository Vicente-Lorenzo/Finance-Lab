import polars as pl

from Library.Dataclass import *
from Library.Database import PostgresAPI

class TradeDatabaseAPI(PostgresAPI):

    @staticmethod
    def _structure_() -> dict:
        return {
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
            TradeAPI.ID.ExitBalance: pl.Float64()
        }
