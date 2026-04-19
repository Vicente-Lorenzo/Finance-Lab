from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Database.Dataframe import pl
from Library.Database.Database import PrimaryKey, ForeignKey
from Library.Database.Datapoint import DatapointAPI
from Library.Database.Dataclass import overridefield
from Library.Market.Market import MarketAPI
from Library.Market.Timestamp import TimestampAPI
from Library.Market.Price import PriceAPI
from Library.Universe.Universe import UniverseAPI
if TYPE_CHECKING:
    from Library.Database import DatabaseAPI
    from Library.Universe.Contract import ContractAPI

class TickMode(Enum):
    Accurate = 0
    Inaccurate = 1

@dataclass(kw_only=True)
class TickAPI(DatapointAPI):

    Database: ClassVar[str] = DatapointAPI.Database
    Schema: ClassVar[str] = MarketAPI.Schema
    Table: ClassVar[str] = "Tick"

    SecurityUID: int | None = None
    DateTime: datetime | None = None
    AskPrice: float | None = None
    BidPrice: float | None = None
    Volume: float | None = None

    AskBaseConversion: float | None = field(default=None, init=True, repr=True)
    BidBaseConversion: float | None = field(default=None, init=True, repr=True)
    AskQuoteConversion: float | None = field(default=None, init=True, repr=True)
    BidQuoteConversion: float | None = field(default=None, init=True, repr=True)

    timestamp: InitVar[datetime | None] = field(default=None, init=True, repr=False)
    ask: InitVar[float | PriceAPI | None] = field(default=None, init=True, repr=False)
    bid: InitVar[float | PriceAPI | None] = field(default=None, init=True, repr=False)

    contract: InitVar[ContractAPI | None] = field(default=None, init=True, repr=False)

    _timestamp_: TimestampAPI | None = field(default=None, init=False, repr=False)
    _ask_: PriceAPI | None = field(default=None, init=False, repr=False)
    _bid_: PriceAPI | None = field(default=None, init=False, repr=False)
    _contract_: ContractAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        from Library.Universe.Security import SecurityAPI
        return {
            cls.ID.SecurityUID: ForeignKey(pl.Int64, reference=f'"{UniverseAPI.Schema}"."{SecurityAPI.Table}"("{SecurityAPI.ID.UID}")', primary=True),
            cls.ID.DateTime: PrimaryKey(pl.Datetime),
            cls.ID.AskPrice: pl.Float64(),
            cls.ID.BidPrice: pl.Float64(),
            cls.ID.Volume: pl.Float64(),
            **DatapointAPI.Structure()
        }

    def __post_init__(self,
                      db: DatabaseAPI | None,
                      timestamp: datetime | None,
                      ask: float | PriceAPI | None,
                      bid: float | PriceAPI | None,
                      contract: ContractAPI | None) -> None:
        if isinstance(contract, property): contract = None
        if isinstance(timestamp, property): timestamp = None
        if isinstance(ask, property): ask = None
        if isinstance(bid, property): bid = None
        self._contract_ = contract
        if timestamp: self.DateTime = timestamp
        if self.DateTime: self._timestamp_ = TimestampAPI(DateTime=self.DateTime)
        if ask is not None or bid is not None:
            if isinstance(ask, PriceAPI) or isinstance(bid, PriceAPI):
                self._ask_ = ask if isinstance(ask, PriceAPI) else None
                self._bid_ = bid if isinstance(bid, PriceAPI) else None
                if self._ask_: self.AskPrice = self._ask_.Price
                if self._bid_: self.BidPrice = self._bid_.Price
            else:
                self.AskPrice = ask
                self.BidPrice = bid
                if self.AskPrice is not None and self.BidPrice is not None:
                    self._ask_ = PriceAPI(Price=self.AskPrice, Reference=self.BidPrice, Contract=self._contract_)
                    self._bid_ = PriceAPI(Price=self.BidPrice, Reference=self.AskPrice, Contract=self._contract_)
        elif self.AskPrice is not None and self.BidPrice is not None:
            self._ask_ = PriceAPI(Price=self.AskPrice, Reference=self.BidPrice, Contract=self._contract_)
            self._bid_ = PriceAPI(Price=self.BidPrice, Reference=self.AskPrice, Contract=self._contract_)
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=self.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def _apply_(self, row: dict) -> None:
        if self.SecurityUID is None: self.SecurityUID = row.get("SecurityUID")
        if self.DateTime is None: self.DateTime = row.get("DateTime")
        if self.AskPrice is None: self.AskPrice = row.get("AskPrice")
        if self.BidPrice is None: self.BidPrice = row.get("BidPrice")
        if self.Volume is None: self.Volume = row.get("Volume")
        if self.DateTime: self._timestamp_ = TimestampAPI(DateTime=self.DateTime)
        if self.AskPrice is not None and self.BidPrice is not None:
            self._ask_ = PriceAPI(Price=self.AskPrice, Reference=self.BidPrice, Contract=self._contract_)
            self._bid_ = PriceAPI(Price=self.BidPrice, Reference=self.AskPrice, Contract=self._contract_)

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = super().pull(condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        if not self.SecurityUID or not self.DateTime: return
        row = super().pull(
            condition='"SecurityUID" = :security: AND "DateTime" = :datetime:',
            parameters={"security": self.SecurityUID, "datetime": self.DateTime}
        )
        if not row: return
        self._apply_(row)

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or [self.ID.SecurityUID, self.ID.DateTime])

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
    def Ask(self) -> PriceAPI | None:
        return self._ask_
    @property
    @overridefield
    def Bid(self) -> PriceAPI | None:
        return self._bid_

    @property
    def Spread(self) -> PriceAPI | None:
        if self.AskPrice is None or self.BidPrice is None: return None
        return PriceAPI(Price=self.AskPrice - self.BidPrice, Reference=self.AskPrice, Contract=self._contract_)

    @property
    def MidPrice(self) -> float | None:
        if self.AskPrice is None or self.BidPrice is None: return None
        return (self.AskPrice + self.BidPrice) / 2

    @property
    def InvertedAsk(self) -> float | None:
        if not self.AskPrice: return None
        return 1.0 / self.AskPrice

    @property
    def InvertedBid(self) -> float | None:
        if not self.BidPrice: return None
        return 1.0 / self.BidPrice

    @property
    @overridefield
    def Contract(self) -> ContractAPI | None:
        return self._contract_
    @Contract.setter
    def Contract(self, contract: ContractAPI | None) -> None:
        self._contract_ = contract
        if self._ask_: self._ask_.Contract = self._contract_
        if self._bid_: self._bid_.Contract = self._contract_