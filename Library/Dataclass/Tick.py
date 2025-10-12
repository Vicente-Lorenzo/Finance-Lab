from enum import Enum
from typing import Union
from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Dataclass import overridefield, DataclassAPI, TimestampAPI, PriceAPI, SymbolAPI
from Library.Utility import cast

class TickMode(Enum):
    Accurate = 0
    Inaccurate = 1

@dataclass(slots=True)
class TickAPI(DataclassAPI):
    Timestamp: InitVar[datetime] = field(default=None, init=True, repr=True)
    Ask: InitVar[Union[float, PriceAPI]] = field(default=None, init=True, repr=True)
    Bid: InitVar[Union[float, PriceAPI]] = field(default=None, init=True, repr=True)
    AskBaseConversion: float = field(default=None, init=True, repr=True)
    BidBaseConversion: float = field(default=None, init=True, repr=True)
    AskQuoteConversion: float = field(default=None, init=True, repr=True)
    BidQuoteConversion: float = field(default=None, init=True, repr=True)

    Symbol: InitVar[SymbolAPI] = field(default=None, init=True, repr=True)

    _Timestamp: TimestampAPI = field(default=None, init=False, repr=False)
    _Ask: PriceAPI = field(default=None, init=False, repr=False)
    _Bid: PriceAPI = field(default=None, init=False, repr=False)

    _Symbol: SymbolAPI = field(default=None, init=False, repr=False)

    def __post_init__(self,
                      timestamp: datetime,
                      ask: Union[float, PriceAPI],
                      bid: Union[float, PriceAPI],
                      symbol: SymbolAPI) -> None:

        self._Symbol = cast(symbol, SymbolAPI, None)
        self._Timestamp = TimestampAPI(Timestamp=cast(timestamp, datetime, None))

        if isinstance(ask, PriceAPI) or isinstance(bid, PriceAPI):
            self._Ask = ask
            self._Bid = bid
        else:
            ask_price = cast(ask, float, None)
            bid_price = cast(bid, float, None)
            self._Ask = PriceAPI(Price=ask_price, Reference=bid_price, Symbol=self._Symbol)
            self._Bid = PriceAPI(Price=bid_price, Reference=ask_price, Symbol=self._Symbol)

    @property
    @overridefield
    def Timestamp(self) -> TimestampAPI:
        return self._Timestamp
    @Timestamp.setter
    def Timestamp(self, timestamp: datetime) -> None:
        self._Timestamp.Timestamp = cast(timestamp, datetime, None)

    @property
    @overridefield
    def Ask(self) -> PriceAPI:
        return self._Ask
    @property
    @overridefield
    def Bid(self) -> PriceAPI:
        return self._Bid

    @property
    def Spread(self) -> PriceAPI:
        return PriceAPI(Price=self._Ask.Price - self._Bid.Price, Reference=self._Ask.Price, Symbol=self._Symbol)

    @property
    @overridefield
    def Symbol(self) -> SymbolAPI:
        return self._Symbol
    @Symbol.setter
    def Symbol(self, symbol) -> None:
        self._Symbol = cast(symbol, float, None)
        self._Ask.Symbol = self._Symbol
        self._Bid.Symbol = self._Symbol
