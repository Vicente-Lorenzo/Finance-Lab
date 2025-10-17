from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Dataclass import overridefield, SymbolAPI, PositionAPI, TimestampAPI
from Library.Utility import cast

@dataclass(slots=True, kw_only=True)
class TradeAPI(PositionAPI):
    TradeID: int = field(init=True, repr=True)
    ExitTimestamp: InitVar[datetime] = field(init=True, repr=False)

    ExitBalance: float = field(default=None, init=True, repr=True)

    _ExitTimestamp: TimestampAPI = field(default=None, init=False, repr=False)

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
                      symbol: SymbolAPI,
                      exit_timestamp: datetime):

        PositionAPI.__post_init__(self,
            entry_timestamp=entry_timestamp,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            max_runup_price=max_runup_price,
            max_drawdown_price=max_drawdown_price,
            exit_price=exit_price,
            stop_loss_pnl=stop_loss_pnl,
            take_profit_pnl=take_profit_pnl,
            max_runup_pnl=max_runup_pnl,
            max_drawdown_pnl=max_drawdown_pnl,
            gross_pnl=gross_pnl,
            commission_pnl=commission_pnl,
            swap_pnl=swap_pnl,
            net_pnl=net_pnl,
            entry_balance=entry_balance,
            symbol=symbol
        )

        self._ExitTimestamp = TimestampAPI(Timestamp=cast(exit_timestamp, datetime, None))

    @property
    @overridefield
    def ExitTimestamp(self) -> TimestampAPI:
        return self._ExitTimestamp
    @ExitTimestamp.setter
    def ExitTimestamp(self, exit_timestamp: datetime) -> None:
        self._ExitTimestamp.Timestamp = cast(exit_timestamp, datetime, None)
