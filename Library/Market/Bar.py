from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Database.Dataframe import pl
from Library.Database.Database import PrimaryKey, ForeignKey
from Library.Database.Datapoint import DatapointAPI
from Library.Database.Dataclass import overridefield
from Library.Market.Market import MarketAPI
from Library.Market.Timestamp import TimestampAPI
from Library.Market.Tick import TickAPI
from Library.Universe.Universe import UniverseAPI
if TYPE_CHECKING: 
    from Library.Database import DatabaseAPI
    from Library.Universe.Contract import ContractAPI

@dataclass(kw_only=True)
class BarAPI(DatapointAPI):

    Database: ClassVar[str] = DatapointAPI.Database
    Schema: ClassVar[str] = MarketAPI.Schema
    Table: ClassVar[str] = "Bar"

    SecurityUID: int | None = None
    TimeframeUID: str | None = None
    DateTime: datetime | None = None

    OpenAskPrice: float | None = None
    OpenBidPrice: float | None = None
    HighAskPrice: float | None = None
    HighBidPrice: float | None = None
    LowAskPrice: float | None = None
    LowBidPrice: float | None = None
    CloseAskPrice: float | None = None
    CloseBidPrice: float | None = None
    TickVolume: float | None = None

    timestamp: InitVar[datetime | None] = field(default=None, init=True, repr=False)

    gap_timestamp: InitVar[datetime | None] = field(default=None, init=True, repr=False)
    gap_ask: InitVar[float | None] = field(default=None, init=True, repr=False)
    gap_bid: InitVar[float | None] = field(default=None, init=True, repr=False)
    gap_ask_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    gap_bid_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    gap_ask_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    gap_bid_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)

    open_timestamp: InitVar[datetime | None] = field(default=None, init=True, repr=False)
    open_ask_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    open_bid_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    open_ask_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    open_bid_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)

    high_timestamp: InitVar[datetime | None] = field(default=None, init=True, repr=False)
    high_ask_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    high_bid_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    high_ask_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    high_bid_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)

    low_timestamp: InitVar[datetime | None] = field(default=None, init=True, repr=False)
    low_ask_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    low_bid_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    low_ask_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    low_bid_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)

    close_timestamp: InitVar[datetime | None] = field(default=None, init=True, repr=False)
    close_ask_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    close_bid_base_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    close_ask_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)
    close_bid_quote_conversion: InitVar[float | None] = field(default=None, init=True, repr=False)

    contract: InitVar[ContractAPI | None] = field(default=None, init=True, repr=False)

    _timestamp_: TimestampAPI | None = field(default=None, init=False, repr=False)
    _gap_tick_: TickAPI | None = field(default=None, init=False, repr=False)
    _open_tick_: TickAPI | None = field(default=None, init=False, repr=False)
    _high_tick_: TickAPI | None = field(default=None, init=False, repr=False)
    _low_tick_: TickAPI | None = field(default=None, init=False, repr=False)
    _close_tick_: TickAPI | None = field(default=None, init=False, repr=False)

    _contract_: ContractAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        from Library.Universe.Security import SecurityAPI
        from Library.Universe.Timeframe import TimeframeAPI
        return {
            cls.ID.SecurityUID: ForeignKey(pl.Int64, reference=f'"{UniverseAPI.Schema}"."{SecurityAPI.Table}"("{SecurityAPI.ID.UID}")', primary=True),
            cls.ID.TimeframeUID: ForeignKey(pl.String, reference=f'"{UniverseAPI.Schema}"."{TimeframeAPI.Table}"("{TimeframeAPI.ID.UID}")', primary=True),
            cls.ID.DateTime: PrimaryKey(pl.Datetime),
            cls.ID.OpenAskPrice: pl.Float64(),
            cls.ID.OpenBidPrice: pl.Float64(),
            cls.ID.HighAskPrice: pl.Float64(),
            cls.ID.HighBidPrice: pl.Float64(),
            cls.ID.LowAskPrice: pl.Float64(),
            cls.ID.LowBidPrice: pl.Float64(),
            cls.ID.CloseAskPrice: pl.Float64(),
            cls.ID.CloseBidPrice: pl.Float64(),
            cls.ID.TickVolume: pl.Float64(),
            **DatapointAPI.Structure()
        }

    def __post_init__(self,
                      db: DatabaseAPI | None,
                      timestamp: datetime | None,
                      gap_timestamp: datetime | None,
                      gap_ask: float | None,
                      gap_bid: float | None,
                      gap_ask_base_conversion: float | None,
                      gap_bid_base_conversion: float | None,
                      gap_ask_quote_conversion: float | None,
                      gap_bid_quote_conversion: float | None,
                      open_timestamp: datetime | None,
                      open_ask_base_conversion: float | None,
                      open_bid_base_conversion: float | None,
                      open_ask_quote_conversion: float | None,
                      open_bid_quote_conversion: float | None,
                      high_timestamp: datetime | None,
                      high_ask_base_conversion: float | None,
                      high_bid_base_conversion: float | None,
                      high_ask_quote_conversion: float | None,
                      high_bid_quote_conversion: float | None,
                      low_timestamp: datetime | None,
                      low_ask_base_conversion: float | None,
                      low_bid_base_conversion: float | None,
                      low_ask_quote_conversion: float | None,
                      low_bid_quote_conversion: float | None,
                      close_timestamp: datetime | None,
                      close_ask_base_conversion: float | None,
                      close_bid_base_conversion: float | None,
                      close_ask_quote_conversion: float | None,
                      close_bid_quote_conversion: float | None,
                      contract: ContractAPI | None) -> None:
        if not isinstance(contract, property) and contract:
            self._contract_ = contract
        if not isinstance(timestamp, property) and timestamp:
            self.DateTime = timestamp
        if self.DateTime:
            self._timestamp_ = TimestampAPI(DateTime=self.DateTime)
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=self.Schema, table=self.Table, structure=self.Structure())
        self.pull()
        self._rebuild_ticks_(
            gap_timestamp, gap_ask, gap_bid, gap_ask_base_conversion, gap_bid_base_conversion, gap_ask_quote_conversion, gap_bid_quote_conversion,
            open_timestamp, open_ask_base_conversion, open_bid_base_conversion, open_ask_quote_conversion, open_bid_quote_conversion,
            high_timestamp, high_ask_base_conversion, high_bid_base_conversion, high_ask_quote_conversion, high_bid_quote_conversion,
            low_timestamp, low_ask_base_conversion, low_bid_base_conversion, low_ask_quote_conversion, low_bid_quote_conversion,
            close_timestamp, close_ask_base_conversion, close_bid_base_conversion, close_ask_quote_conversion, close_bid_quote_conversion
        )

    def _rebuild_ticks_(self, 
            gap_timestamp, gap_ask, gap_bid, gap_ask_base_conversion, gap_bid_base_conversion, gap_ask_quote_conversion, gap_bid_quote_conversion,
            open_timestamp, open_ask_base_conversion, open_bid_base_conversion, open_ask_quote_conversion, open_bid_quote_conversion,
            high_timestamp, high_ask_base_conversion, high_bid_base_conversion, high_ask_quote_conversion, high_bid_quote_conversion,
            low_timestamp, low_ask_base_conversion, low_bid_base_conversion, low_ask_quote_conversion, low_bid_quote_conversion,
            close_timestamp, close_ask_base_conversion, close_bid_base_conversion, close_ask_quote_conversion, close_bid_quote_conversion
        ):
        def get_val(val, default):
            return val if not isinstance(val, property) and val is not None else default
        dt = self.DateTime
        if get_val(gap_ask, None) is not None and get_val(gap_bid, None) is not None:
            self._gap_tick_ = TickAPI(
                SecurityUID=self.SecurityUID,
                DateTime=get_val(gap_timestamp, dt),
                AskPrice=gap_ask,
                BidPrice=gap_bid,
                AskBaseConversion=get_val(gap_ask_base_conversion, None),
                BidBaseConversion=get_val(gap_bid_base_conversion, None),
                AskQuoteConversion=get_val(gap_ask_quote_conversion, None),
                BidQuoteConversion=get_val(gap_bid_quote_conversion, None),
                db=self._db_
            )
            self._gap_tick_.Contract = self._contract_
        if self.OpenAskPrice is not None and self.OpenBidPrice is not None:
            self._open_tick_ = TickAPI(
                SecurityUID=self.SecurityUID,
                DateTime=get_val(open_timestamp, dt),
                AskPrice=self.OpenAskPrice,
                BidPrice=self.OpenBidPrice,
                AskBaseConversion=get_val(open_ask_base_conversion, None),
                BidBaseConversion=get_val(open_bid_base_conversion, None),
                AskQuoteConversion=get_val(open_ask_quote_conversion, None),
                BidQuoteConversion=get_val(open_bid_quote_conversion, None),
                db=self._db_
            )
            self._open_tick_.Contract = self._contract_
        if self.HighAskPrice is not None and self.HighBidPrice is not None:
            self._high_tick_ = TickAPI(
                SecurityUID=self.SecurityUID,
                DateTime=get_val(high_timestamp, dt),
                AskPrice=self.HighAskPrice,
                BidPrice=self.HighBidPrice,
                AskBaseConversion=get_val(high_ask_base_conversion, None),
                BidBaseConversion=get_val(high_bid_base_conversion, None),
                AskQuoteConversion=get_val(high_ask_quote_conversion, None),
                BidQuoteConversion=get_val(high_bid_quote_conversion, None),
                db=self._db_
            )
            self._high_tick_.Contract = self._contract_
        if self.LowAskPrice is not None and self.LowBidPrice is not None:
            self._low_tick_ = TickAPI(
                SecurityUID=self.SecurityUID,
                DateTime=get_val(low_timestamp, dt),
                AskPrice=self.LowAskPrice,
                BidPrice=self.LowBidPrice,
                AskBaseConversion=get_val(low_ask_base_conversion, None),
                BidBaseConversion=get_val(low_bid_base_conversion, None),
                AskQuoteConversion=get_val(low_ask_quote_conversion, None),
                BidQuoteConversion=get_val(low_bid_quote_conversion, None),
                db=self._db_
            )
            self._low_tick_.Contract = self._contract_
        if self.CloseAskPrice is not None and self.CloseBidPrice is not None:
            self._close_tick_ = TickAPI(
                SecurityUID=self.SecurityUID,
                DateTime=get_val(close_timestamp, dt),
                AskPrice=self.CloseAskPrice,
                BidPrice=self.CloseBidPrice,
                AskBaseConversion=get_val(close_ask_base_conversion, None),
                BidBaseConversion=get_val(close_bid_base_conversion, None),
                AskQuoteConversion=get_val(close_ask_quote_conversion, None),
                BidQuoteConversion=get_val(close_bid_quote_conversion, None),
                db=self._db_
            )
            self._close_tick_.Contract = self._contract_

    def _apply_(self, row: dict) -> None:
        if self.SecurityUID is None: self.SecurityUID = row.get("SecurityUID")
        if self.TimeframeUID is None: self.TimeframeUID = row.get("TimeframeUID")
        if self.DateTime is None: self.DateTime = row.get("DateTime")
        if self.OpenAskPrice is None: self.OpenAskPrice = row.get("OpenAskPrice")
        if self.OpenBidPrice is None: self.OpenBidPrice = row.get("OpenBidPrice")
        if self.HighAskPrice is None: self.HighAskPrice = row.get("HighAskPrice")
        if self.HighBidPrice is None: self.HighBidPrice = row.get("HighBidPrice")
        if self.LowAskPrice is None: self.LowAskPrice = row.get("LowAskPrice")
        if self.LowBidPrice is None: self.LowBidPrice = row.get("LowBidPrice")
        if self.CloseAskPrice is None: self.CloseAskPrice = row.get("CloseAskPrice")
        if self.CloseBidPrice is None: self.CloseBidPrice = row.get("CloseBidPrice")
        if self.TickVolume is None: self.TickVolume = row.get("TickVolume")
        if self.DateTime: self._timestamp_ = TimestampAPI(DateTime=self.DateTime)

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = super().pull(condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        if not self.SecurityUID or not self.TimeframeUID or not self.DateTime: return
        row = super().pull(
            condition='"SecurityUID" = :security: AND "TimeframeUID" = :timeframe: AND "DateTime" = :datetime:',
            parameters={"security": self.SecurityUID, "timeframe": self.TimeframeUID, "datetime": self.DateTime}
        )
        if not row: return
        self._apply_(row)

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or [self.ID.SecurityUID, self.ID.TimeframeUID, self.ID.DateTime])

    @property
    @overridefield
    def Timestamp(self) -> TimestampAPI | None:
        return self._timestamp_
    @Timestamp.setter
    def Timestamp(self, timestamp: datetime) -> None:
        self.DateTime = timestamp
        if self._timestamp_: self._timestamp_.DateTime = timestamp
        else: self._timestamp_ = TimestampAPI(DateTime=timestamp)

    @property
    @overridefield
    def GapTick(self) -> TickAPI | None:
        return self._gap_tick_
    @property
    @overridefield
    def OpenTick(self) -> TickAPI | None:
        return self._open_tick_
    @property
    @overridefield
    def HighTick(self) -> TickAPI | None:
        return self._high_tick_
    @property
    @overridefield
    def LowTick(self) -> TickAPI | None:
        return self._low_tick_
    @property
    @overridefield
    def CloseTick(self) -> TickAPI | None:
        return self._close_tick_
    @property
    def RangeTick(self) -> TickAPI | None:
        if not self._open_tick_ or not self._high_tick_ or not self._low_tick_: return None
        return TickAPI(
            SecurityUID=self.SecurityUID,
            DateTime=self._open_tick_.DateTime,
            AskPrice=self._high_tick_.AskPrice - self._low_tick_.AskPrice,
            BidPrice=self._high_tick_.BidPrice - self._low_tick_.BidPrice,
            AskBaseConversion=self._open_tick_.AskBaseConversion,
            BidBaseConversion=self._open_tick_.BidBaseConversion,
            AskQuoteConversion=self._open_tick_.AskQuoteConversion,
            BidQuoteConversion=self._open_tick_.BidQuoteConversion,
            db=self._db_
        )

    @property
    def MidOpen(self) -> float | None:
        if self.OpenAskPrice is None or self.OpenBidPrice is None: return None
        return (self.OpenAskPrice + self.OpenBidPrice) / 2
    @property
    def MidHigh(self) -> float | None:
        if self.HighAskPrice is None or self.HighBidPrice is None: return None
        return (self.HighAskPrice + self.HighBidPrice) / 2
    @property
    def MidLow(self) -> float | None:
        if self.LowAskPrice is None or self.LowBidPrice is None: return None
        return (self.LowAskPrice + self.LowBidPrice) / 2
    @property
    def MidClose(self) -> float | None:
        if self.CloseAskPrice is None or self.CloseBidPrice is None: return None
        return (self.CloseAskPrice + self.CloseBidPrice) / 2

    @property
    def RangeHighLow(self) -> float | None:
        if self.MidHigh is None or self.MidLow is None: return None
        return self.MidHigh - self.MidLow
    @property
    def RangeOpenClose(self) -> float | None:
        if self.MidClose is None or self.MidOpen is None: return None
        return self.MidClose - self.MidOpen
    
    @property
    def InvertedOpenAsk(self) -> float | None:
        if not self.OpenAskPrice: return None
        return 1.0 / self.OpenAskPrice
    @property
    def InvertedOpenBid(self) -> float | None:
        if not self.OpenBidPrice: return None
        return 1.0 / self.OpenBidPrice
    @property
    def InvertedCloseAsk(self) -> float | None:
        if not self.CloseAskPrice: return None
        return 1.0 / self.CloseAskPrice
    @property
    def InvertedCloseBid(self) -> float | None:
        if not self.CloseBidPrice: return None
        return 1.0 / self.CloseBidPrice

    @property
    @overridefield
    def Contract(self) -> ContractAPI | None:
        return self._contract_
    @Contract.setter
    def Contract(self, contract: ContractAPI | None) -> None:
        self._contract_ = contract
        if self._gap_tick_: self._gap_tick_.Contract = self._contract_
        if self._open_tick_: self._open_tick_.Contract = self._contract_
        if self._high_tick_: self._high_tick_.Contract = self._contract_
        if self._low_tick_: self._low_tick_.Contract = self._contract_
        if self._close_tick_: self._close_tick_.Contract = self._contract_