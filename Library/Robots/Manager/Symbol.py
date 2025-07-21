from Library.Classes import AssetType, CommissionMode, SwapMode, DayOfWeek, Symbol, Bar

class SymbolAPI:

    def __init__(self):
        self.BaseAsset: AssetType | None = None
        self.QuoteAsset: AssetType | None = None
        self.Digits: int | None = None
        self.PipSize: float | None = None
        self.PointSize: float | None = None
        self.LotSize: int | None = None
        self.VolumeInUnitsMin: float | None = None
        self.VolumeInUnitsMax: float | None = None
        self.VolumeInUnitsStep: float | None = None
        self.Commission: float | None = None
        self.CommissionMode: CommissionMode | None = None
        self.SwapLong: float | None = None
        self.SwapShort: float | None = None
        self.SwapMode: SwapMode | None = None
        self.SwapExtraDay: DayOfWeek | None = None
        
        self.PipValue: float | None = None
        self.TickValue: float | None = None

    def init_symbol(self, symbol: Symbol) -> None:
        self.BaseAsset = symbol.BaseAsset
        self.QuoteAsset = symbol.QuoteAsset
        self.Digits = symbol.Digits
        self.PipSize = symbol.PipSize
        self.PointSize = symbol.PointSize
        self.LotSize = symbol.LotSize
        self.VolumeInUnitsMin = symbol.VolumeInUnitsMin
        self.VolumeInUnitsMax = symbol.VolumeInUnitsMax
        self.VolumeInUnitsStep = symbol.VolumeInUnitsStep
        self.Commission = symbol.Commission
        self.CommissionMode = symbol.CommissionMode
        self.SwapLong = symbol.SwapLong
        self.SwapShort = symbol.SwapShort
        self.SwapMode = symbol.SwapMode
        self.SwapExtraDay = symbol.SwapExtraDay

    def update_symbol(self, bar: Bar) -> None:
        self.PipValue = self.PipSize * self.LotSize / bar.ClosePrice
        self.TickValue = self.PipValue / 10

    def data(self) -> Symbol:
        return Symbol(
            BaseAsset=self.BaseAsset,
            QuoteAsset=self.QuoteAsset,
            Digits=self.Digits,
            PointSize=self.PointSize,
            PipSize=self.PipSize,
            LotSize=self.LotSize,
            VolumeInUnitsMin=self.VolumeInUnitsMin,
            VolumeInUnitsMax=self.VolumeInUnitsMax,
            VolumeInUnitsStep=self.VolumeInUnitsStep,
            Commission=self.Commission,
            CommissionMode=self.CommissionMode,
            SwapLong=self.SwapLong,
            SwapShort=self.SwapShort,
            SwapMode=self.SwapMode,
            SwapExtraDay=self.SwapExtraDay
        )

    def __repr__(self):
        return repr(self.data())