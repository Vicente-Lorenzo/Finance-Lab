import polars as pl

from Library.Dataclass import *
from Library.Database import PostgresAPI

class SymbolDatabaseAPI(PostgresAPI):

    STRUCTURE: dict = {
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
