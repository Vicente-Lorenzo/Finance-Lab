import math
import talib

from Agents.Container.Enums import TechnicalType
from Agents.Container.Classes import Technical

class Technicals:

    @classmethod
    def find(cls, technical_type: TechnicalType) -> dict[str, Technical]:
        return {technical_id: technical for technical_id, technical in cls.__dict__.items() if isinstance(technical, Technical) and technical.TechnicalType == technical_type}

    # ==================== BASELINES ====================
    SMA = Technical(
        Name="Simple Moving Average (Short-Term)",
        TechnicalType=TechnicalType.Baseline,
        Input=lambda market: [market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.SMA(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.Result, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.Result, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.Result, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.Result, shift))

    EMA = Technical(
        Name="Exponential Moving Average",
        TechnicalType=TechnicalType.Baseline,
        Input=lambda market: [market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.EMA(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.Result, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.Result, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.Result, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.Result, shift))

    WMA = Technical(
        Name="Weighted Moving Average",
        TechnicalType=TechnicalType.Baseline,
        Input=lambda market: [market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.WMA(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.Result, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.Result, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.Result, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.Result, shift))

    @staticmethod
    def custom_HMA(series, window):
        return talib.WMA(2 * talib.WMA(*series, timeperiod=math.floor(window / 2)) - talib.WMA(*series, timeperiod=window), timeperiod=math.floor(math.sqrt(window)))


    HMA = Technical(
        Name="Hull Moving Average",
        TechnicalType=TechnicalType.Baseline,
        Input=lambda market: [market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: Technicals.custom_HMA(series, window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.Result, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.Result, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.Result, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.Result, shift))

    DEMA = Technical(
        Name="Double Exponential Moving Average",
        TechnicalType=TechnicalType.Baseline,
        Input=lambda market: [market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.DEMA(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.Result, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.Result, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.Result, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.Result, shift))

    TEMA = Technical(
        Name="Triple Exponential Moving Average",
        TechnicalType=TechnicalType.Baseline,
        Input=lambda market: [market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.TEMA(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.Result, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.Result, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.Result, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.Result, shift))
    
    TRIMA = Technical(
        Name="Triangular Moving Average",
        TechnicalType=TechnicalType.Baseline,
        Input=lambda market: [market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.TRIMA(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.Result, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.Result, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.Result, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.Result, shift))

    KAMA = Technical(
        Name="Kaufman Adaptive Moving Average",
        TechnicalType=TechnicalType.Baseline,
        Input=lambda market: [market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.KAMA(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.Result, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.Result, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.Result, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.Result, shift))

    # ==================== OVERLAP ====================
    SMAC = Technical(
        Name="Simple Moving Average Cross",
        TechnicalType=TechnicalType.Overlap,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (talib.SMA(*series, timeperiod=fast_window), talib.SMA(*series, timeperiod=slow_window)),
        Output=["Fast", "Slow"],
        FilterBuy=lambda _, technical, shift: technical.Fast.over(technical.Slow),
        FilterSell=lambda _, technical, shift: technical.Fast.under(technical.Slow),
        SignalBuy=lambda _, technical, shift: technical.Fast.crossover(technical.Slow),
        SignalSell=lambda _, technical, shift: technical.Fast.crossunder(technical.Slow))


    EMAC = Technical(
        Name="Exponential Moving Average Cross",
        TechnicalType=TechnicalType.Overlap,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (talib.EMA(*series, timeperiod=fast_window), talib.EMA(*series, timeperiod=slow_window)),
        Output=["Fast", "Slow"],
        FilterBuy=lambda _, technical, shift: technical.Fast.over(technical.Slow),
        FilterSell=lambda _, technical, shift: technical.Fast.under(technical.Slow),
        SignalBuy=lambda _, technical, shift: technical.Fast.crossover(technical.Slow),
        SignalSell=lambda _, technical, shift: technical.Fast.crossunder(technical.Slow))

    WMAC = Technical(
        Name="Weighted Moving Average Cross",
        TechnicalType=TechnicalType.Overlap,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (talib.WMA(*series, timeperiod=fast_window), talib.WMA(*series, timeperiod=slow_window)),
        Output=["Fast", "Slow"],
        FilterBuy=lambda _, technical, shift: technical.Fast.over(technical.Slow),
        FilterSell=lambda _, technical, shift: technical.Fast.under(technical.Slow),
        SignalBuy=lambda _, technical, shift: technical.Fast.crossover(technical.Slow),
        SignalSell=lambda _, technical, shift: technical.Fast.crossunder(technical.Slow))

    HMAC = Technical(
        Name="Hull Moving Average Cross",
        TechnicalType=TechnicalType.Overlap,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (Technicals.custom_HMA(series, fast_window), Technicals.custom_HMA(series, slow_window)),
        Output=["Fast", "Slow"],
        FilterBuy=lambda _, technical, shift: technical.Fast.over(technical.Slow),
        FilterSell=lambda _, technical, shift: technical.Fast.under(technical.Slow),
        SignalBuy=lambda _, technical, shift: technical.Fast.crossover(technical.Slow),
        SignalSell=lambda _, technical, shift: technical.Fast.crossunder(technical.Slow))

    DEMAC = Technical(
        Name="Double Exponential Moving Average Cross",
        TechnicalType=TechnicalType.Overlap,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (talib.DEMA(*series, timeperiod=fast_window), talib.DEMA(*series, timeperiod=slow_window)),
        Output=["Fast", "Slow"],
        FilterBuy=lambda _, technical, shift: technical.Fast.over(technical.Slow),
        FilterSell=lambda _, technical, shift: technical.Fast.under(technical.Slow),
        SignalBuy=lambda _, technical, shift: technical.Fast.crossover(technical.Slow),
        SignalSell=lambda _, technical, shift: technical.Fast.crossunder(technical.Slow))

    TEMAC = Technical(
        Name="Triple Exponential Moving Average Cross",
        TechnicalType=TechnicalType.Overlap,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (talib.TEMA(*series, timeperiod=fast_window), talib.TEMA(*series, timeperiod=slow_window)),
        Output=["Fast", "Slow"],
        FilterBuy=lambda _, technical, shift: technical.Fast.over(technical.Slow),
        FilterSell=lambda _, technical, shift: technical.Fast.under(technical.Slow),
        SignalBuy=lambda _, technical, shift: technical.Fast.crossover(technical.Slow),
        SignalSell=lambda _, technical, shift: technical.Fast.crossunder(technical.Slow))

    TRIMAC = Technical(
        Name="Triangular Moving Average Cross",
        TechnicalType=TechnicalType.Overlap,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (talib.TRIMA(*series, timeperiod=fast_window), talib.TRIMA(*series, timeperiod=slow_window)),
        Output=["Fast", "Slow"],
        FilterBuy=lambda _, technical, shift: technical.Fast.over(technical.Slow),
        FilterSell=lambda _, technical, shift: technical.Fast.under(technical.Slow),
        SignalBuy=lambda _, technical, shift: technical.Fast.crossover(technical.Slow),
        SignalSell=lambda _, technical, shift: technical.Fast.crossunder(technical.Slow))

    KAMAC = Technical(
        Name="Kaufman Adaptive Moving Average Cross",
        TechnicalType=TechnicalType.Overlap,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (talib.KAMA(*series, timeperiod=fast_window), talib.KAMA(*series, timeperiod=slow_window)),
        Output=["Fast", "Slow"],
        FilterBuy=lambda _, technical, shift: technical.Fast.over(technical.Slow),
        FilterSell=lambda _, technical, shift: technical.Fast.under(technical.Slow),
        SignalBuy=lambda _, technical, shift: technical.Fast.crossover(technical.Slow),
        SignalSell=lambda _, technical, shift: technical.Fast.crossunder(technical.Slow))

    # ==================== Momentum ====================

    AROON = Technical(
        Name="Aroon Up and Down Indicator",
        TechnicalType=TechnicalType.Momentum,
        Input=lambda market: [market.HighPrice, market.LowPrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.AROON(*series, timeperiod=window),
        Output=["Down", "Up"],
        FilterBuy=lambda _, technical, shift: technical.Up.over(technical.Down),
        FilterSell=lambda _, technical, shift: technical.Down.over(technical.Up),
        SignalBuy=lambda _, technical, shift: technical.Up.crossover(technical.Down),
        SignalSell=lambda _, technical, shift: technical.Down.crossunder(technical.Up))

    CCI = Technical(
        Name="Commodity Channel Index",
        TechnicalType=TechnicalType.Momentum,
        Input=lambda market: [market.HighPrice, market.LowPrice, market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.CCI(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda _, technical, shift: technical.Result.over(0, shift),
        FilterSell=lambda _, technical, shift: technical.Result.under(0, shift),
        SignalBuy=lambda _, technical, shift: technical.Result.crossover(0, shift),
        SignalSell=lambda _, technical, shift: technical.Result.crossunder(0, shift))

    MACD = Technical(
        Name="Moving Average Convergence Divergence",
        TechnicalType=TechnicalType.Momentum,
        Input=lambda market: [market.ClosePrice],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "signal_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window, signal_window: fast_window >= 5 and slow_window >= 5 and signal_window >= 5 and signal_window < fast_window and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window, signal_window: talib.MACD(*series, fastperiod=fast_window, slowperiod=slow_window, signalperiod=signal_window),
        Output=["MACD", "Signal", "Histogram"],
        FilterBuy=lambda _, technical, shift: technical.MACD.over(technical.Signal, shift),
        FilterSell=lambda _, technical, shift: technical.MACD.under(technical.Signal, shift),
        SignalBuy=lambda _, technical, shift: technical.MACD.crossover(technical.Signal, shift),
        SignalSell=lambda _, technical, shift: technical.MACD.crossunder(technical.Signal, shift))

    PSAR = Technical(
        Name="Parabolic SAR",
        TechnicalType=TechnicalType.Momentum,
        Input=lambda market: [market.HighPrice, market.LowPrice],
        Parameters={"acceleration": [[0.01, 0.2, 0.01], [-0.05, +0.05, 0.01], [-0.02, +0.02, 0.01]], "maximum": [[0.1, 0.5, 0.05], [-0.1, +0.1, 0.01], [-0.05, +0.05, 0.01]]},
        Constraints=lambda acceleration, maximum: acceleration > 0.0 and maximum > 0.0 and acceleration < maximum,
        Function=lambda series, acceleration, maximum: talib.SAR(*series, acceleration=acceleration, maximum=maximum),
        Output=["PSAR"],
        FilterBuy=lambda market, technical, shift: market.ClosePrice.over(technical.PSAR, shift),
        FilterSell=lambda market, technical, shift: market.ClosePrice.under(technical.PSAR, shift),
        SignalBuy=lambda market, technical, shift: market.ClosePrice.crossover(technical.PSAR, shift),
        SignalSell=lambda market, technical, shift: market.ClosePrice.crossunder(technical.PSAR, shift))

    # BBANDS = Technical(
    #     Name="Bollinger Bands",
    #     TechnicalType=TechnicalType.Volatility,
    #     Input=lambda market: [market.ClosePrice],
    #     Parameters={"period": [5, 300, 1], "nbdevup": [1.0, 3.0, 0.1], "nbdevdn": [1.0, 3.0, 0.1], "matype": [0, 1, 2, 3, 4]},
    #     Constraints=lambda period, nbdevup, nbdevdn, matype: True,
    #     Function=talib.BBANDS,
    #     Output=["Upper", "Middle", "Lower"],
    #     FilterBuy=lambda market, technical, shift: False,
    #     FilterSell=lambda market, technical, shift: False,
    #     SignalBuy=lambda market, technical, shift: False,
    #     SignalSell=lambda market, technical, shift: False)

    # ==================== Volume ====================
    # AD = Technical(
    #     Name="Chaikin A/D Line",
    #     TechnicalType=TechnicalType.Volume,
    #     Input=lambda market: [market.HighPrice, market.LowPrice, market.ClosePrice, market.Volume],
    #     Parameters={},
    #     Constraints=lambda: True,
    #     Function=lambda series: (talib.AD(*series),),
    #     Output=["AD"],
    #     FilterBuy=lambda _, technical, shift: technical.AD.rising(),
    #     FilterSell=lambda _, technical, shift: technical.AD.falling(),
    #     SignalBuy=lambda _, technical, shift: technical.AD.crossup(technical.AD.sma(10)),
    #     SignalSell=lambda _, technical, shift: technical.AD.crossdown(technical.AD.sma(10)))

    ADOSC = Technical(
        Name="Chaikin A/D Oscillator",
        TechnicalType=TechnicalType.Volume,
        Input=lambda market: [market.HighPrice, market.LowPrice, market.ClosePrice, market.TickVolume],
        Parameters={"fast_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]], "slow_window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda fast_window, slow_window: fast_window >= 5 and slow_window >= 5 and fast_window < slow_window,
        Function=lambda series, fast_window, slow_window: (talib.ADOSC(*series, fastperiod=fast_window, slowperiod=slow_window),),
        Output=["ADOSC"],
        FilterBuy=lambda _, technical, shift: technical.ADOSC.over(0.0, shift),
        FilterSell=lambda _, technical, shift: technical.ADOSC.over(0.0, shift),
        SignalBuy=lambda _, technical, shift: technical.ADOSC.crossover(0.0, shift),
        SignalSell=lambda _, technical, shift: technical.ADOSC.crossover(0.0, shift))

    # OBV = Technical(
    #     Name="On Balance Volume",
    #     TechnicalType=TechnicalType.Volume,
    #     Input=lambda market: [market.ClosePrice, market.Volume],
    #     Parameters={},
    #     Constraints=lambda: True,
    #     Function=lambda series: (talib.OBV(*series),),
    #     Output=["OBV"],
    #     FilterBuy=lambda _, technical, shift: technical.OBV.rising(),
    #     FilterSell=lambda _, technical, shift: technical.OBV.falling(),
    #     SignalBuy=lambda _, technical, shift: technical.OBV.crossup(technical.OBV.sma(10)),
    #     SignalSell=lambda _, technical, shift: technical.OBV.crossdown(technical.OBV.sma(10)))

    # ==================== Volatility ====================
    ATR = Technical(
        Name="Average True Range",
        TechnicalType=TechnicalType.Volatility,
        Input=lambda market: [market.HighPrice, market.LowPrice, market.ClosePrice],
        Parameters={"window": [[5, 50, 5], [-20, +20, 2], [-10, +10, 1]]},
        Constraints=lambda window: window >= 5,
        Function=lambda series, window: talib.ATR(*series, timeperiod=window),
        Output=["Result"],
        FilterBuy=lambda market, technical, shift: False,
        FilterSell=lambda market, technical, shift: False,
        SignalBuy=lambda market, technical, shift: False,
        SignalSell=lambda market, technical, shift: False)

    # ==================== Other ====================
    TT = Technical(
        Name="True Filter and True Signal",
        TechnicalType=TechnicalType.Other,
        Input=lambda market: [market.ClosePrice],
        Parameters={},
        Constraints=lambda _: True,
        Function=lambda series: series,
        Output=["Result"],
        FilterBuy=lambda *_: True,
        FilterSell=lambda *_: True,
        SignalBuy=lambda *_: True,
        SignalSell=lambda*_: True)

    TF = Technical(
        Name="True Filter and False Signal",
        TechnicalType=TechnicalType.Other,
        Input=lambda market: [market.ClosePrice],
        Parameters={},
        Constraints=lambda _: True,
        Function=lambda series: series,
        Output=["Result"],
        FilterBuy=lambda *_: True,
        FilterSell=lambda *_: True,
        SignalBuy=lambda *_: False,
        SignalSell=lambda*_: False)

    FT = Technical(
        Name="False Filter and True Signal",
        TechnicalType=TechnicalType.Other,
        Input=lambda market: [market.ClosePrice],
        Parameters={},
        Constraints=lambda _: True,
        Function=lambda series: series,
        Output=["Result"],
        FilterBuy=lambda *_: False,
        FilterSell=lambda *_: False,
        SignalBuy=lambda *_: True,
        SignalSell=lambda*_: True)

    FF = Technical(
        Name="False Filter and False Signal",
        TechnicalType=TechnicalType.Other,
        Input=lambda market: [market.ClosePrice],
        Parameters={},
        Constraints=lambda _: True,
        Function=lambda series: series,
        Output=["Result"],
        FilterBuy=lambda *_: False,
        FilterSell=lambda *_: False,
        SignalBuy=lambda *_: False,
        SignalSell=lambda*_: False)