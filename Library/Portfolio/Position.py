from __future__ import annotations

from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Utility.Dataclass import overridefield, DataclassAPI
from Library.Market.Timestamp import TimestampAPI
from Library.Market.Price import PriceAPI
from Library.Portfolio.PnL import PnLAPI
from Library.Universe.Symbol import SymbolAPI

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

    _entry_timestamp_: TimestampAPI = field(default=None, init=False, repr=False)

    _entry_price_: PriceAPI = field(default=None, init=False, repr=False)
    _stop_loss_price_: PriceAPI = field(default=None, init=False, repr=False)
    _take_profit_price_: PriceAPI = field(default=None, init=False, repr=False)
    _max_run_up_price_: PriceAPI = field(default=None, init=False, repr=False)
    _max_draw_down_price_: PriceAPI = field(default=None, init=False, repr=False)
    _exit_price_: PriceAPI = field(default=None, init=False, repr=False)

    _stop_loss_pn_l_: PnLAPI = field(default=None, init=False, repr=False)
    _take_profit_pn_l_: PnLAPI = field(default=None, init=False, repr=False)
    _max_draw_down_pn_l_: PnLAPI = field(default=None, init=False, repr=False)
    _max_run_up_pn_l_: PnLAPI = field(default=None, init=False, repr=False)
    _gross_pn_l_: PnLAPI = field(default=None, init=False, repr=False)
    _commission_pn_l_: PnLAPI = field(default=None, init=False, repr=False)
    _swap_pn_l_: PnLAPI = field(default=None, init=False, repr=False)
    _net_pn_l_: PnLAPI = field(default=None, init=False, repr=False)

    _entry_balance_: float = field(default=None, init=False, repr=False)

    _symbol_: SymbolAPI = field(default=None, init=False, repr=False)

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

        self._symbol_ = symbol
        self._entry_balance_ = entry_balance

        self._entry_timestamp_ = TimestampAPI(DateTime=entry_timestamp)

        self._entry_price_ = PriceAPI(Price=entry_price, Reference=entry_price, Symbol=self._symbol_)
        self._stop_loss_price_ = PriceAPI(Price=stop_loss_price, Reference=entry_price, Symbol=self._symbol_)
        self._take_profit_price_ = PriceAPI(Price=take_profit_price, Reference=entry_price, Symbol=self._symbol_)
        self._max_run_up_price_ = PriceAPI(Price=max_runup_price, Reference=entry_price, Symbol=self._symbol_)
        self._max_draw_down_price_ = PriceAPI(Price=max_drawdown_price, Reference=entry_price, Symbol=self._symbol_)
        self._exit_price_ = PriceAPI(Price=exit_price, Reference=entry_price, Symbol=self._symbol_)

        self._stop_loss_pn_l_ = PnLAPI(PnL=stop_loss_pnl, Reference=self._entry_balance_)
        self._take_profit_pn_l_ = PnLAPI(PnL=take_profit_pnl, Reference=self._entry_balance_)
        self._max_run_up_pn_l_ = PnLAPI(PnL=max_runup_pnl, Reference=self._entry_balance_)
        self._max_draw_down_pn_l_ = PnLAPI(PnL=max_drawdown_pnl, Reference=self._entry_balance_)
        self._gross_pn_l_ = PnLAPI(PnL=gross_pnl, Reference=self._entry_balance_)
        self._commission_pn_l_ = PnLAPI(PnL=commission_pnl, Reference=self._entry_balance_)
        self._swap_pn_l_ = PnLAPI(PnL=swap_pnl, Reference=self._entry_balance_)
        self._net_pn_l_ = PnLAPI(PnL=net_pnl, Reference=self._entry_balance_)

    @property
    @overridefield
    def EntryTimestamp(self) -> TimestampAPI:
        return self._entry_timestamp_
    @EntryTimestamp.setter
    def EntryTimestamp(self, entry_timestamp: datetime) -> None:
        self._entry_timestamp_.DateTime = entry_timestamp

    @property
    @overridefield
    def EntryPrice(self) -> PriceAPI:
        return self._entry_price_
    @EntryPrice.setter
    def EntryPrice(self, entry_price: float) -> None:
        entry_price = entry_price
        self._entry_price_.Price = entry_price
        self._entry_price_.Reference = entry_price
        self._stop_loss_price_.Reference = entry_price
        self._take_profit_price_.Reference = entry_price
        self._max_run_up_price_.Reference = entry_price
        self._max_draw_down_price_.Reference = entry_price
        self._exit_price_.Reference = entry_price
    @property
    @overridefield
    def StopLossPrice(self) -> PriceAPI:
        return self._stop_loss_price_
    @StopLossPrice.setter
    def StopLossPrice(self, stop_loss_price: float) -> None:
        self._stop_loss_price_.Price = stop_loss_price
    @property
    @overridefield
    def TakeProfitPrice(self) -> PriceAPI:
        return self._take_profit_price_
    @TakeProfitPrice.setter
    def TakeProfitPrice(self, take_profit_price: float) -> None:
        self._take_profit_price_.Price = take_profit_price
    @property
    @overridefield
    def MaxRunUpPrice(self) -> PriceAPI:
        return self._max_run_up_price_
    @MaxRunUpPrice.setter
    def MaxRunUpPrice(self, max_runup_price: float) -> None:
        self._max_run_up_price_.Price = max_runup_price
    @property
    @overridefield
    def MaxDrawDownPrice(self) -> PriceAPI:
        return self._max_draw_down_price_
    @MaxDrawDownPrice.setter
    def MaxDrawDownPrice(self, max_drawdown_price: float) -> None:
        self._max_draw_down_price_.Price = max_drawdown_price
    @property
    @overridefield
    def ExitPrice(self) -> PriceAPI:
        return self._exit_price_
    @ExitPrice.setter
    def ExitPrice(self, exit_price: float) -> None:
        self._exit_price_.Price = exit_price

    @property
    @overridefield
    def StopLossPnL(self) -> PnLAPI:
        return self._stop_loss_pn_l_
    @StopLossPnL.setter
    def StopLossPnL(self, stop_loss_pnl: float) -> None:
        self._stop_loss_pn_l_.PnL = stop_loss_pnl
    @property
    @overridefield
    def TakeProfitPnL(self) -> PnLAPI:
        return self._take_profit_pn_l_
    @TakeProfitPnL.setter
    def TakeProfitPnL(self, take_profit_pnl: float) -> None:
        self._take_profit_pn_l_.PnL = take_profit_pnl
    @property
    @overridefield
    def MaxRunUpPnL(self) -> PnLAPI:
        return self._max_run_up_pn_l_
    @MaxRunUpPnL.setter
    def MaxRunUpPnL(self, max_runup_pnl: float) -> None:
        self._max_run_up_pn_l_.PnL = max_runup_pnl
    @property
    @overridefield
    def MaxDrawDownPnL(self) -> PnLAPI:
        return self._max_draw_down_pn_l_
    @MaxDrawDownPnL.setter
    def MaxDrawDownPnL(self, max_drawdown_pnl: float) -> None:
        self._max_draw_down_pn_l_.PnL = max_drawdown_pnl
    @property
    @overridefield
    def GrossPnL(self) -> PnLAPI:
        return self._gross_pn_l_
    @GrossPnL.setter
    def GrossPnL(self, gross_pnl: float) -> None:
        self._gross_pn_l_.PnL = gross_pnl
    @property
    @overridefield
    def CommissionPnL(self) -> PnLAPI:
        return self._commission_pn_l_
    @CommissionPnL.setter
    def CommissionPnL(self, commission_pnl: float) -> None:
        self._commission_pn_l_.PnL = commission_pnl
    @property
    @overridefield
    def SwapPnL(self) -> PnLAPI:
        return self._swap_pn_l_
    @SwapPnL.setter
    def SwapPnL(self, swap_pnl: float) -> None:
        self._swap_pn_l_.PnL = swap_pnl
    @property
    @overridefield
    def NetPnL(self) -> PnLAPI:
        return self._net_pn_l_
    @NetPnL.setter
    def NetPnL(self, net_pnl: float) -> None:
        self._net_pn_l_.PnL = net_pnl

    @property
    @overridefield
    def EntryBalance(self) -> float:
        return self._entry_balance_
    @EntryBalance.setter
    def EntryBalance(self, entry_balance: float) -> None:
        self._entry_balance_ = entry_balance
        self._stop_loss_pn_l_.Reference = entry_balance
        self._take_profit_pn_l_.Reference = entry_balance
        self._max_run_up_pn_l_.Reference = entry_balance
        self._max_draw_down_pn_l_.Reference = entry_balance
        self._gross_pn_l_.Reference = entry_balance
        self._commission_pn_l_.Reference = entry_balance
        self._swap_pn_l_.Reference = entry_balance
        self._net_pn_l_.Reference = entry_balance

    @property
    @overridefield
    def Symbol(self) -> SymbolAPI:
        return self._symbol_
    @Symbol.setter
    def Symbol(self, symbol: SymbolAPI) -> None:
        self._symbol_ = symbol
        self._entry_price_.Symbol = self._symbol_
        self._stop_loss_price_.Symbol = self._symbol_
        self._take_profit_price_.Symbol = self._symbol_
        self._max_run_up_price_.Symbol = self._symbol_
        self._max_draw_down_price_.Symbol = self._symbol_
        self._exit_price_.Symbol = self._symbol_
