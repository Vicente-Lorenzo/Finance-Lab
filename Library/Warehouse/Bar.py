import polars as pl

from Library.Dataclass import *
from Library.Database import PostgresAPI

class BarDatabaseAPI(PostgresAPI):

    STRUCTURE: dict = {
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
