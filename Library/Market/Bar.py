from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from dataclasses import dataclass, field, InitVar

from Library.Database.Dataclass import overridefield, DataclassAPI
from Library.Market.Timestamp import TimestampAPI
from Library.Market.Price import PriceAPI
from Library.Market.Tick import TickAPI
if TYPE_CHECKING: from Library.Universe.Contract import ContractAPI

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

    Contract: InitVar[ContractAPI] = field(default=None, init=True, repr=False)

    _timestamp_: TimestampAPI = field(default=None, init=False, repr=False)
    _gap_tick_: TickAPI = field(default=None, init=False, repr=False)
    _open_tick_: TickAPI = field(default=None, init=False, repr=False)
    _high_tick_: TickAPI = field(default=None, init=False, repr=False)
    _low_tick_: TickAPI = field(default=None, init=False, repr=False)
    _close_tick_: TickAPI = field(default=None, init=False, repr=False)

    _contract_: ContractAPI = field(default=None, init=False, repr=False)

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
                      contract: ContractAPI) -> None:

        self._contract_ = contract
        self._timestamp_ = TimestampAPI(DateTime=timestamp)

        self._gap_tick_ = TickAPI(
            Timestamp=gap_timestamp,
            Ask=PriceAPI(Price=gap_ask, Reference=gap_ask, Contract=self._contract_),
            Bid=PriceAPI(Price=gap_bid, Reference=gap_bid, Contract=self._contract_),
            AskBaseConversion=gap_ask_base_conversion,
            BidBaseConversion=gap_bid_base_conversion,
            AskQuoteConversion=gap_ask_quote_conversion,
            BidQuoteConversion=gap_bid_quote_conversion
        )
        self._open_tick_ = TickAPI(
            Timestamp=open_timestamp,
            Ask=PriceAPI(Price=open_ask, Reference=gap_ask, Contract=self._contract_),
            Bid=PriceAPI(Price=open_bid, Reference=gap_bid, Contract=self._contract_),
            AskBaseConversion=open_ask_base_conversion,
            BidBaseConversion=open_bid_base_conversion,
            AskQuoteConversion=open_ask_quote_conversion,
            BidQuoteConversion=open_bid_quote_conversion
        )
        self._high_tick_ = TickAPI(
            Timestamp=high_timestamp,
            Ask=PriceAPI(Price=high_ask, Reference=open_ask, Contract=self._contract_),
            Bid=PriceAPI(Price=high_bid, Reference=open_bid, Contract=self._contract_),
            AskBaseConversion=high_ask_base_conversion,
            BidBaseConversion=high_bid_base_conversion,
            AskQuoteConversion=high_ask_quote_conversion,
            BidQuoteConversion=high_bid_quote_conversion
        )
        self._low_tick_ = TickAPI(
            Timestamp=low_timestamp,
            Ask=PriceAPI(Price=low_ask, Reference=open_ask, Contract=self._contract_),
            Bid=PriceAPI(Price=low_bid, Reference=open_bid, Contract=self._contract_),
            AskBaseConversion=low_ask_base_conversion,
            BidBaseConversion=low_bid_base_conversion,
            AskQuoteConversion=low_ask_quote_conversion,
            BidQuoteConversion=low_bid_quote_conversion
        )
        self._close_tick_ = TickAPI(
            Timestamp=close_timestamp,
            Ask=PriceAPI(Price=close_ask, Reference=open_ask, Contract=self._contract_),
            Bid=PriceAPI(Price=close_bid, Reference=open_bid, Contract=self._contract_),
            AskBaseConversion=close_ask_base_conversion,
            BidBaseConversion=close_bid_base_conversion,
            AskQuoteConversion=close_ask_quote_conversion,
            BidQuoteConversion=close_bid_quote_conversion
        )

    @property
    @overridefield
    def Timestamp(self) -> TimestampAPI:
        return self._timestamp_

    @property
    @overridefield
    def GapTick(self) -> TickAPI:
        return self._gap_tick_
    @property
    @overridefield
    def OpenTick(self) -> TickAPI:
        return self._open_tick_
    @property
    @overridefield
    def HighTick(self) -> TickAPI:
        return self._high_tick_
    @property
    @overridefield
    def LowTick(self) -> TickAPI:
        return self._low_tick_
    @property
    @overridefield
    def CloseTick(self) -> TickAPI:
        return self._close_tick_
    @property
    def RangeTick(self) -> TickAPI:
        return TickAPI(
            Timestamp=self._open_tick_.Timestamp.DateTime,
            Ask=PriceAPI(self._high_tick_.Ask.Price - self._low_tick_.Ask.Price, Reference=self._open_tick_.Ask.Price, Contract=self._contract_),
            Bid=PriceAPI(self._high_tick_.Bid.Price - self._low_tick_.Bid.Price, Reference=self._open_tick_.Bid.Price, Contract=self._contract_),
            AskBaseConversion=self._open_tick_.AskBaseConversion,
            BidBaseConversion=self._open_tick_.BidBaseConversion,
            AskQuoteConversion=self._open_tick_.AskQuoteConversion,
            BidQuoteConversion=self._open_tick_.BidQuoteConversion
        )

    @property
    @overridefield
    def Contract(self) -> ContractAPI:
        return self._contract_
    @Contract.setter
    def Contract(self, contract) -> None:
        self._contract_ = contract
        self._gap_tick_.Contract = self._contract_
        self._open_tick_.Contract = self._contract_
        self._high_tick_.Contract = self._contract_
        self._low_tick_.Contract = self._contract_
        self._close_tick_.Contract = self._contract_
