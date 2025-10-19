from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Dataclass import overridefield, DataclassAPI, TimestampAPI, PriceAPI, SymbolAPI, TickAPI
from Library.Utility import cast

@dataclass(slots=True)
class BarAPI(DataclassAPI):
    Timestamp: InitVar[datetime] = field(default=None, init=True, repr=False)

    GapTimestamp: InitVar[datetime] = field(default=None, init=True, repr=False)
    GapAsk: InitVar[float] = field(default=None, init=True, repr=False)
    GapBid: InitVar[float] = field(default=None, init=True, repr=False)
    GapAskBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    GapBidBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    GapAskQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)
    GapBidQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)

    OpenTimestamp: InitVar[datetime] = field(default=None, init=True, repr=False)
    OpenAsk: InitVar[float] = field(default=None, init=True, repr=False)
    OpenBid: InitVar[float] = field(default=None, init=True, repr=False)
    OpenAskBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    OpenBidBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    OpenAskQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)
    OpenBidQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)

    HighTimestamp: InitVar[datetime] = field(default=None, init=True, repr=False)
    HighAsk: InitVar[float] = field(default=None, init=True, repr=False)
    HighBid: InitVar[float] = field(default=None, init=True, repr=False)
    HighAskBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    HighBidBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    HighAskQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)
    HighBidQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)

    LowTimestamp: InitVar[datetime] = field(default=None, init=True, repr=False)
    LowAsk: InitVar[float] = field(default=None, init=True, repr=False)
    LowBid: InitVar[float] = field(default=None, init=True, repr=False)
    LowAskBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    LowBidBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    LowAskQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)
    LowBidQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)

    CloseTimestamp: InitVar[datetime] = field(default=None, init=True, repr=False)
    CloseAsk: InitVar[float] = field(default=None, init=True, repr=False)
    CloseBid: InitVar[float] = field(default=None, init=True, repr=False)
    CloseAskBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    CloseBidBaseConversion: InitVar[float] = field(default=None, init=True, repr=False)
    CloseAskQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)
    CloseBidQuoteConversion: InitVar[float] = field(default=None, init=True, repr=False)

    TickVolume: float = field(default=None, init=True, repr=True)

    Symbol: InitVar[SymbolAPI] = field(default=None, init=True, repr=False)

    _Timestamp: TimestampAPI = field(default=None, init=False, repr=False)
    _GapTick: TickAPI = field(default=None, init=False, repr=False)
    _OpenTick: TickAPI = field(default=None, init=False, repr=False)
    _HighTick: TickAPI = field(default=None, init=False, repr=False)
    _LowTick: TickAPI = field(default=None, init=False, repr=False)
    _CloseTick: TickAPI = field(default=None, init=False, repr=False)

    _Symbol: SymbolAPI = field(default=None, init=False, repr=False)

    def __post_init__(self,
                      timestamp: datetime,
                      gap_timestamp: datetime,
                      gap_ask: float,
                      gap_bid: float,
                      gap_ask_base_conversion: float,
                      gap_bid_base_conversion: float,
                      gap_ask_quote_conversion: float,
                      gap_bid_quote_conversion: float,
                      open_timestamp: datetime,
                      open_ask: float,
                      open_bid: float,
                      open_ask_base_conversion: float,
                      open_bid_base_conversion: float,
                      open_ask_quote_conversion: float,
                      open_bid_quote_conversion: float,
                      high_timestamp: datetime,
                      high_ask: float,
                      high_bid: float,
                      high_ask_base_conversion: float,
                      high_bid_base_conversion: float,
                      high_ask_quote_conversion: float,
                      high_bid_quote_conversion: float,
                      low_timestamp: datetime,
                      low_ask: float,
                      low_bid: float,
                      low_ask_base_conversion: float,
                      low_bid_base_conversion: float,
                      low_ask_quote_conversion: float,
                      low_bid_quote_conversion: float,
                      close_timestamp: datetime,
                      close_ask: float,
                      close_bid: float,
                      close_ask_base_conversion: float,
                      close_bid_base_conversion: float,
                      close_ask_quote_conversion: float,
                      close_bid_quote_conversion: float,
                      symbol: SymbolAPI) -> None:

        self._Symbol = cast(symbol, SymbolAPI, None)
        self._Timestamp = TimestampAPI(DateTime=cast(timestamp, datetime, None))

        self._GapTick = TickAPI(
            Timestamp=cast(gap_timestamp, datetime, None),
            Ask=PriceAPI(Price=(gap_ask := cast(gap_ask, float, None)), Reference=gap_ask, Symbol=self._Symbol),
            Bid=PriceAPI(Price=(gap_bid := cast(gap_bid, float, None)), Reference=gap_bid, Symbol=self._Symbol),
            AskBaseConversion=cast(gap_ask_base_conversion, float, None),
            BidBaseConversion=cast(gap_bid_base_conversion, float, None),
            AskQuoteConversion=cast(gap_ask_quote_conversion, float, None),
            BidQuoteConversion=cast(gap_bid_quote_conversion, float, None)
        )
        self._OpenTick = TickAPI(
            Timestamp=cast(open_timestamp, datetime, None),
            Ask=PriceAPI(Price=(open_ask := cast(open_ask, float, None)), Reference=gap_ask, Symbol=self._Symbol),
            Bid=PriceAPI(Price=(open_bid := cast(open_bid, float, None)), Reference=gap_bid, Symbol=self._Symbol),
            AskBaseConversion=cast(open_ask_base_conversion, float, None),
            BidBaseConversion=cast(open_bid_base_conversion, float, None),
            AskQuoteConversion=cast(open_ask_quote_conversion, float, None),
            BidQuoteConversion=cast(open_bid_quote_conversion, float, None)
        )
        self._HighTick = TickAPI(
            Timestamp=cast(high_timestamp, datetime, None),
            Ask=PriceAPI(Price=cast(high_ask, float, None), Reference=open_ask, Symbol=self._Symbol),
            Bid=PriceAPI(Price=cast(high_bid, float, None), Reference=open_bid, Symbol=self._Symbol),
            AskBaseConversion=cast(high_ask_base_conversion, float, None),
            BidBaseConversion=cast(high_bid_base_conversion, float, None),
            AskQuoteConversion=cast(high_ask_quote_conversion, float, None),
            BidQuoteConversion=cast(high_bid_quote_conversion, float, None)
        )
        self._LowTick = TickAPI(
            Timestamp=cast(low_timestamp, datetime, None),
            Ask=PriceAPI(Price=cast(low_ask, float, None), Reference=open_ask, Symbol=self._Symbol),
            Bid=PriceAPI(Price=cast(low_bid, float, None), Reference=open_bid, Symbol=self._Symbol),
            AskBaseConversion=cast(low_ask_base_conversion, float, None),
            BidBaseConversion=cast(low_bid_base_conversion, float, None),
            AskQuoteConversion=cast(low_ask_quote_conversion, float, None),
            BidQuoteConversion=cast(low_bid_quote_conversion, float, None)
        )
        self._CloseTick = TickAPI(
            Timestamp=cast(close_timestamp, datetime, None),
            Ask=PriceAPI(Price=cast(close_ask, float, None), Reference=open_ask, Symbol=self._Symbol),
            Bid=PriceAPI(Price=cast(close_bid, float, None), Reference=open_bid, Symbol=self._Symbol),
            AskBaseConversion=cast(close_ask_base_conversion, float, None),
            BidBaseConversion=cast(close_bid_base_conversion, float, None),
            AskQuoteConversion=cast(close_ask_quote_conversion, float, None),
            BidQuoteConversion=cast(close_bid_quote_conversion, float, None)
        )

    @property
    @overridefield
    def Timestamp(self) -> TimestampAPI:
        return self._Timestamp

    @property
    @overridefield
    def GapTick(self) -> TickAPI:
        return self._GapTick
    @property
    @overridefield
    def OpenTick(self) -> TickAPI:
        return self._OpenTick
    @property
    @overridefield
    def HighTick(self) -> TickAPI:
        return self._HighTick
    @property
    @overridefield
    def LowTick(self) -> TickAPI:
        return self._LowTick
    @property
    @overridefield
    def CloseTick(self) -> TickAPI:
        return self._CloseTick
    @property
    def RangeTick(self) -> TickAPI:
        return TickAPI(
            Timestamp=self._OpenTick.Timestamp.DateTime,
            Ask=PriceAPI(self._HighTick.Ask.Price - self._LowTick.Ask.Price, Reference=self._OpenTick.Ask.Price, Symbol=self._Symbol),
            Bid=PriceAPI(self._HighTick.Bid.Price - self._LowTick.Bid.Price, Reference=self._OpenTick.Bid.Price, Symbol=self._Symbol),
            AskBaseConversion=self._OpenTick.AskBaseConversion,
            BidBaseConversion=self._OpenTick.BidBaseConversion,
            AskQuoteConversion=self._OpenTick.AskQuoteConversion,
            BidQuoteConversion=self._OpenTick.BidQuoteConversion
        )

    @property
    @overridefield
    def Symbol(self) -> SymbolAPI:
        return self._Symbol
    @Symbol.setter
    def Symbol(self, symbol) -> None:
        self._Symbol = cast(symbol, float, None)
        self._GapTick.Symbol = self._Symbol
        self._OpenTick.Symbol = self._Symbol
        self._HighTick.Symbol = self._Symbol
        self._LowTick.Symbol = self._Symbol
        self._CloseTick.Symbol = self._Symbol
