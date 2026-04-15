from __future__ import annotations

from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Utility.Dataclass import overridefield, DataclassAPI
from Library.Market.Timestamp import TimestampAPI
from Library.Market.Price import PriceAPI
from Library.Universe.Symbol import SymbolAPI

class TickMode(Enum):
    Accurate = 0
    Inaccurate = 1

@dataclass(slots=True)
class TickAPI(DataclassAPI):
    Timestamp: InitVar[datetime] = field(default=None, init=True, repr=False)
    Ask: InitVar[float | PriceAPI] = field(default=None, init=True, repr=False)
    Bid: InitVar[float | PriceAPI] = field(default=None, init=True, repr=False)
    AskBaseConversion: float = field(default=None, init=True, repr=True)
    BidBaseConversion: float = field(default=None, init=True, repr=True)
    AskQuoteConversion: float = field(default=None, init=True, repr=True)
    BidQuoteConversion: float = field(default=None, init=True, repr=True)

    Symbol: InitVar[SymbolAPI] = field(default=None, init=True, repr=False)

    _timestamp_: TimestampAPI = field(default=None, init=False, repr=False)
    _ask_: PriceAPI = field(default=None, init=False, repr=False)
    _bid_: PriceAPI = field(default=None, init=False, repr=False)

    _symbol_: SymbolAPI = field(default=None, init=False, repr=False)

    def __post_init__(self,
                      timestamp: datetime,
                      ask: float | PriceAPI,
                      bid: float | PriceAPI,
                      symbol: SymbolAPI) -> None:

        self._symbol_ = symbol
        self._timestamp_ = TimestampAPI(DateTime=timestamp)

        if isinstance(ask, PriceAPI) or isinstance(bid, PriceAPI):
            self._ask_ = ask
            self._bid_ = bid
        else:
            ask_price = ask
            bid_price = bid
            self._ask_ = PriceAPI(Price=ask_price, Reference=bid_price, Symbol=self._symbol_)
            self._bid_ = PriceAPI(Price=bid_price, Reference=ask_price, Symbol=self._symbol_)

    @property
    @overridefield
    def Timestamp(self) -> TimestampAPI:
        return self._timestamp_
    @Timestamp.setter
    def Timestamp(self, timestamp: datetime) -> None:
        self._timestamp_.DateTime = timestamp

    @property
    @overridefield
    def Ask(self) -> PriceAPI:
        return self._ask_
    @property
    @overridefield
    def Bid(self) -> PriceAPI:
        return self._bid_

    @property
    def Spread(self) -> PriceAPI:
        return PriceAPI(Price=self._ask_.Price - self._bid_.Price, Reference=self._ask_.Price, Symbol=self._symbol_)

    @property
    @overridefield
    def Symbol(self) -> SymbolAPI:
        return self._symbol_
    @Symbol.setter
    def Symbol(self, symbol) -> None:
        self._symbol_ = symbol
        self._ask_.Symbol = self._symbol_
        self._bid_.Symbol = self._symbol_
