from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Dataclass import overridefield, DataclassAPI, TimestampAPI, PriceAPI, PnLAPI, SymbolAPI
from Library.Utility import cast

class PositionType(Enum):
    Normal = 0
    Continuation = 1

class TradeType(Enum):
    Buy = 0
    Sell = 1

@dataclass(slots=True, kw_only=True)
class PositionAPI(DataclassAPI):
    PositionID: int = field(init=True, repr=True)
    PositionType: PositionType = field(init=True, repr=True)
    TradeType: TradeType = field(init=True, repr=True)
    Volume: float = field(init=True, repr=True)
    Quantity: float = field(init=True, repr=True)

    EntryTimestamp: InitVar[datetime] = field(init=True, repr=False)

    EntryPrice: InitVar[float] = field(init=True, repr=False)
    StopLossPrice: InitVar[float] = field(default=None, init=True, repr=False)
    TakeProfitPrice: InitVar[float] = field(default=None, init=True, repr=False)
    MaxRunUpPrice: InitVar[float] = field(default=None, init=True, repr=False)
    MaxDrawDownPrice: InitVar[float] = field(default=None, init=True, repr=False)
    ExitPrice: InitVar[float] = field(init=True, repr=False)

    StopLossPnL: InitVar[float] = field(default=None, init=True, repr=False)
    TakeProfitPnL: InitVar[float] = field(default=None, init=True, repr=False)
    MaxRunUpPnL: InitVar[float] = field(default=None, init=True, repr=False)
    MaxDrawDownPnL: InitVar[float] = field(default=None, init=True, repr=False)
    GrossPnL: InitVar[float] = field(init=True, repr=False)
    CommissionPnL: InitVar[float] = field(init=True, repr=False)
    SwapPnL: InitVar[float] = field(init=True, repr=False)
    NetPnL: InitVar[float] = field(init=True, repr=False)

    UsedMargin: float = field(default=None, init=True, repr=True)
    EntryBalance: InitVar[float] = field(default=None, init=True, repr=False)
    MidBalance: float = field(default=None, init=True, repr=True)

    Symbol: InitVar[SymbolAPI] = field(default=None, init=True, repr=False)

    _EntryTimestamp: TimestampAPI = field(default=None, init=False, repr=False)

    _EntryPrice: PriceAPI = field(default=None, init=False, repr=False)
    _StopLossPrice: PriceAPI = field(default=None, init=False, repr=False)
    _TakeProfitPrice: PriceAPI = field(default=None, init=False, repr=False)
    _MaxRunUpPrice: PriceAPI = field(default=None, init=False, repr=False)
    _MaxDrawDownPrice: PriceAPI = field(default=None, init=False, repr=False)
    _ExitPrice: PriceAPI = field(default=None, init=False, repr=False)

    _StopLossPnL: PnLAPI = field(default=None, init=False, repr=False)
    _TakeProfitPnL: PnLAPI = field(default=None, init=False, repr=False)
    _MaxDrawDownPnL: PnLAPI = field(default=None, init=False, repr=False)
    _MaxRunUpPnL: PnLAPI = field(default=None, init=False, repr=False)
    _GrossPnL: PnLAPI = field(default=None, init=False, repr=False)
    _CommissionPnL: PnLAPI = field(default=None, init=False, repr=False)
    _SwapPnL: PnLAPI = field(default=None, init=False, repr=False)
    _NetPnL: PnLAPI = field(default=None, init=False, repr=False)

    _EntryBalance: float = field(default=None, init=False, repr=False)

    _Symbol: SymbolAPI = field(default=None, init=False, repr=False)

    def __post_init__(self,
                      entry_timestamp: datetime,
                      entry_price: float,
                      stop_loss_price: float,
                      take_profit_price: float,
                      max_runup_price: float,
                      max_drawdown_price: float,
                      exit_price: float,
                      stop_loss_pnl: float,
                      take_profit_pnl: float,
                      max_runup_pnl: float,
                      max_drawdown_pnl: float,
                      gross_pnl: float,
                      commission_pnl: float,
                      swap_pnl: float,
                      net_pnl: float,
                      entry_balance: float,
                      symbol: SymbolAPI):

        self.PositionType = PositionType(self.PositionType)
        self.TradeType = TradeType(self.TradeType)

        self._Symbol = cast(symbol, SymbolAPI, None)
        self._EntryBalance = cast(entry_balance, float, None)

        self._EntryTimestamp = TimestampAPI(DateTime=cast(entry_timestamp, datetime, None))

        self._EntryPrice = PriceAPI(Price=(entry_price := cast(entry_price, float, None)), Reference=entry_price, Symbol=self._Symbol)
        self._StopLossPrice = PriceAPI(Price=cast(stop_loss_price, float, None), Reference=entry_price, Symbol=self._Symbol)
        self._TakeProfitPrice = PriceAPI(Price=cast(take_profit_price, float, None), Reference=entry_price, Symbol=self._Symbol)
        self._MaxRunUpPrice = PriceAPI(Price=cast(max_runup_price, float, None), Reference=entry_price, Symbol=self._Symbol)
        self._MaxDrawDownPrice = PriceAPI(Price=cast(max_drawdown_price, float, None), Reference=entry_price, Symbol=self._Symbol)
        self._ExitPrice = PriceAPI(Price=cast(exit_price, float, None), Reference=entry_price, Symbol=self._Symbol)

        self._StopLossPnL = PnLAPI(PnL=cast(stop_loss_pnl, float, None), Reference=self._EntryBalance)
        self._TakeProfitPnL = PnLAPI(PnL=cast(take_profit_pnl, float, None), Reference=self._EntryBalance)
        self._MaxRunUpPnL = PnLAPI(PnL=cast(max_runup_pnl, float, None), Reference=self._EntryBalance)
        self._MaxDrawDownPnL = PnLAPI(PnL=cast(max_drawdown_pnl, float, None), Reference=self._EntryBalance)
        self._GrossPnL = PnLAPI(PnL=cast(gross_pnl, float, None), Reference=self._EntryBalance)
        self._CommissionPnL = PnLAPI(PnL=cast(commission_pnl, float, None), Reference=self._EntryBalance)
        self._SwapPnL = PnLAPI(PnL=cast(swap_pnl, float, None), Reference=self._EntryBalance)
        self._NetPnL = PnLAPI(PnL=cast(net_pnl, float, None), Reference=self._EntryBalance)

    @property
    @overridefield
    def EntryTimestamp(self) -> TimestampAPI:
        return self._EntryTimestamp
    @EntryTimestamp.setter
    def EntryTimestamp(self, entry_timestamp: datetime) -> None:
        self._EntryTimestamp.DateTime = cast(entry_timestamp, datetime, None)

    @property
    @overridefield
    def EntryPrice(self) -> PriceAPI:
        return self._EntryPrice
    @EntryPrice.setter
    def EntryPrice(self, entry_price: float) -> None:
        entry_price = cast(entry_price, float, None)
        self._EntryPrice.Price = entry_price
        self._EntryPrice.Reference = entry_price
        self._StopLossPrice.Reference = entry_price
        self._TakeProfitPrice.Reference = entry_price
        self._MaxRunUpPrice.Reference = entry_price
        self._MaxDrawDownPrice.Reference = entry_price
        self._ExitPrice.Reference = entry_price
    @property
    @overridefield
    def StopLossPrice(self) -> PriceAPI:
        return self._StopLossPrice
    @StopLossPrice.setter
    def StopLossPrice(self, stop_loss_price: float) -> None:
        self._StopLossPrice.Price = cast(stop_loss_price, float, None)
    @property
    @overridefield
    def TakeProfitPrice(self) -> PriceAPI:
        return self._TakeProfitPrice
    @TakeProfitPrice.setter
    def TakeProfitPrice(self, take_profit_price: float) -> None:
        self._TakeProfitPrice.Price = cast(take_profit_price, float, None)
    @property
    @overridefield
    def MaxRunUpPrice(self) -> PriceAPI:
        return self._MaxRunUpPrice
    @MaxRunUpPrice.setter
    def MaxRunUpPrice(self, max_runup_price: float) -> None:
        self._MaxRunUpPrice.Price = cast(max_runup_price, float, None)
    @property
    @overridefield
    def MaxDrawDownPrice(self) -> PriceAPI:
        return self._MaxDrawDownPrice
    @MaxDrawDownPrice.setter
    def MaxDrawDownPrice(self, max_drawdown_price: float) -> None:
        self._MaxDrawDownPrice.Price = cast(max_drawdown_price, float, None)
    @property
    @overridefield
    def ExitPrice(self) -> PriceAPI:
        return self._ExitPrice
    @ExitPrice.setter
    def ExitPrice(self, exit_price: float) -> None:
        self._ExitPrice.Price = cast(exit_price, float, None)

    @property
    @overridefield
    def StopLossPnL(self) -> PnLAPI:
        return self._StopLossPnL
    @StopLossPnL.setter
    def StopLossPnL(self, stop_loss_pnl: float) -> None:
        self._StopLossPnL.PnL = cast(stop_loss_pnl, float, None)
    @property
    @overridefield
    def TakeProfitPnL(self) -> PnLAPI:
        return self._TakeProfitPnL
    @TakeProfitPnL.setter
    def TakeProfitPnL(self, take_profit_pnl: float) -> None:
        self._TakeProfitPnL.PnL = cast(take_profit_pnl, float, None)
    @property
    @overridefield
    def MaxRunUpPnL(self) -> PnLAPI:
        return self._MaxRunUpPnL
    @MaxRunUpPnL.setter
    def MaxRunUpPnL(self, max_runup_pnl: float) -> None:
        self._MaxRunUpPnL.PnL = cast(max_runup_pnl, float, None)
    @property
    @overridefield
    def MaxDrawDownPnL(self) -> PnLAPI:
        return self._MaxDrawDownPnL
    @MaxDrawDownPnL.setter
    def MaxDrawDownPnL(self, max_drawdown_pnl: float) -> None:
        self._MaxDrawDownPnL.PnL = cast(max_drawdown_pnl, float, None)
    @property
    @overridefield
    def GrossPnL(self) -> PnLAPI:
        return self._GrossPnL
    @GrossPnL.setter
    def GrossPnL(self, gross_pnl: float) -> None:
        self._GrossPnL.PnL = cast(gross_pnl, float, None)
    @property
    @overridefield
    def CommissionPnL(self) -> PnLAPI:
        return self._CommissionPnL
    @CommissionPnL.setter
    def CommissionPnL(self, commission_pnl: float) -> None:
        self._CommissionPnL.PnL = cast(commission_pnl, float, None)
    @property
    @overridefield
    def SwapPnL(self) -> PnLAPI:
        return self._SwapPnL
    @SwapPnL.setter
    def SwapPnL(self, swap_pnl: float) -> None:
        self._SwapPnL.PnL = cast(swap_pnl, float, None)
    @property
    @overridefield
    def NetPnL(self) -> PnLAPI:
        return self._NetPnL
    @NetPnL.setter
    def NetPnL(self, net_pnl: float) -> None:
        self._NetPnL.PnL = cast(net_pnl, float, None)

    @property
    @overridefield
    def EntryBalance(self) -> float:
        return self._EntryBalance
    @EntryBalance.setter
    def EntryBalance(self, entry_balance: float) -> None:
        self._EntryBalance = cast(entry_balance, float, None)
        self._StopLossPnL.Reference = entry_balance
        self._TakeProfitPnL.Reference = entry_balance
        self._MaxRunUpPnL.Reference = entry_balance
        self._MaxDrawDownPnL.Reference = entry_balance
        self._GrossPnL.Reference = entry_balance
        self._CommissionPnL.Reference = entry_balance
        self._SwapPnL.Reference = entry_balance
        self._NetPnL.Reference = entry_balance

    @property
    @overridefield
    def Symbol(self) -> SymbolAPI:
        return self._Symbol
    @Symbol.setter
    def Symbol(self, symbol: SymbolAPI) -> None:
        self._Symbol = cast(symbol, SymbolAPI, None)
        self._EntryPrice.Symbol = self._Symbol
        self._StopLossPrice.Symbol = self._Symbol
        self._TakeProfitPrice.Symbol = self._Symbol
        self._MaxRunUpPrice.Symbol = self._Symbol
        self._MaxDrawDownPrice.Symbol = self._Symbol
        self._ExitPrice.Symbol = self._Symbol
