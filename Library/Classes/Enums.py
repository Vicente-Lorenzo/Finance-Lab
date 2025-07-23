from enum import Enum

class VerboseType(Enum):
    Silent = 0
    Critical = 1
    Error = 2
    Warning = 3
    Alert = 4
    Info = 5
    Debug = 6

class AssetType(Enum):
    USD = 0
    EUR = 1
    GBP = 2
    CAD = 3
    JPY = 4
    AUD = 5
    NZD = 6
    CHF = 7
    Other = 8

class FeesType(Enum):
    Points = 0
    Pips = 1
    Percentage = 2
    Amount = 3
    Accurate = 4

class SpreadType(Enum):
    Points = FeesType.Points.value
    Pips = FeesType.Pips.value
    Percentage = FeesType.Percentage.value
    Accurate = FeesType.Accurate.value

class CommissionType(Enum):
    Points = FeesType.Points.value
    Pips = FeesType.Pips.value
    Percentage = FeesType.Percentage.value
    Amount = FeesType.Amount.value
    Accurate = FeesType.Accurate.value

class CommissionMode(Enum):
    UsdPerMillionUsdVolume = 0
    UsdPerOneLot = 1
    PercentageOfTradingVolume = 2
    QuoteCurrencyPerOneLot = 3

class SwapType(Enum):
    Points = FeesType.Points.value
    Pips = FeesType.Pips.value
    Percentage = FeesType.Percentage.value
    Amount = FeesType.Amount.value
    Accurate = FeesType.Accurate.value

class SwapMode(Enum):
    Pips = 0
    Percentage = 1

class DayOfWeek(Enum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6

class PositionType(Enum):
    Normal = 0
    Continuation = 1

class TradeType(Enum):
    Buy = 0
    Sell = 1

class StrategyType(Enum):
    Download = 0
    NNFX = 1
    DDPG = 2

class SystemType(Enum):
    Realtime = 0
    Backtesting = 1
    Optimisation = 2
    Learning = 3

class ManagerType(Enum):
    Investing = 0
    Netting = 1
    Hedging = 2

class TechnicalType(Enum):
    Baseline = 0
    Overlap = 1
    Momentum = 2
    Volume = 3
    Volatility = 4
    Pattern = 5
    Other = 6

class TechnicalMode(Enum):
    Off = 0
    Filter = 1
    Signal = 2
