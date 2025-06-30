from Library.Classes import AssetType, CommissionType, SwapType, DayOfWeek, Symbol, Bar

class SymbolAPI:

    def __init__(self):
        self.BaseAsset: AssetType | None = None
        self.QuoteAsset: AssetType | None = None
        self.Digits: int | None = None
        self.PipSize: float | None = None
        self.TickSize: float | None = None
        self.LotSize: int | None = None
        self.VolumeInUnitsMin: float | None = None
        self.VolumeInUnitsMax: float | None = None
        self.VolumeInUnitsStep: float | None = None
        self.Commission: float | None = None
        self.CommissionType: CommissionType | None = None
        self.SwapLong: float | None = None
        self.SwapShort: float | None = None
        self.SwapType: SwapType | None = None
        self.SwapExtraDay: DayOfWeek | None = None
        
        self.PipValue: float | None = None
        self.TickValue: float | None = None

    def init_symbol(self, symbol: Symbol) -> None:
        self.BaseAsset = symbol.BaseAsset
        self.QuoteAsset = symbol.QuoteAsset
        self.Digits = symbol.Digits
        self.PipSize = symbol.PipSize
        self.TickSize = symbol.TickSize
        self.LotSize = symbol.LotSize
        self.VolumeInUnitsMin = symbol.VolumeInUnitsMin
        self.VolumeInUnitsMax = symbol.VolumeInUnitsMax
        self.VolumeInUnitsStep = symbol.VolumeInUnitsStep
        self.Commission = symbol.Commission
        self.CommissionType = symbol.CommissionType
        self.SwapLong = symbol.SwapLong
        self.SwapShort = symbol.SwapShort
        self.SwapType = symbol.SwapType
        self.SwapExtraDay = symbol.SwapExtraDay

    def update_symbol(self, bar: Bar) -> None:
        self.PipValue = self.PipSize * self.LotSize / bar.ClosePrice
        self.TickValue = self.PipValue / 10

    def data(self) -> Symbol:
        return Symbol(self.BaseAsset,
                      self.QuoteAsset,
                      self.Digits,
                      self.PipSize,
                      self.TickSize,
                      self.LotSize,
                      self.VolumeInUnitsMin,
                      self.VolumeInUnitsMax,
                      self.VolumeInUnitsStep,
                      self.Commission,
                      self.CommissionType,
                      self.SwapLong,
                      self.SwapShort,
                      self.SwapType,
                      self.SwapExtraDay)

    def __repr__(self):
        return repr(self.data())