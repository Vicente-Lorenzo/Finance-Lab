from enum import Enum

class ServiceURI(str, Enum):
    REFDATA = "//blp/refdata"
    MKTDATA = "//blp/mktdata"
    BQL = "//blp/bql"

class RequestType(str, Enum):
    REFERENCE_DATA = "ReferenceDataRequest"
    HISTORICAL_DATA = "HistoricalDataRequest"
    INTRADAY_BAR = "IntradayBarRequest"
    INTRADAY_TICK = "IntradayTickRequest"
    BQL_DATA = "BqlRequest"

class Periodicity(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class EventType(str, Enum):
    TRADE = "TRADE"
    BID = "BID"
    ASK = "ASK"
    BID_BEST = "BID_BEST"
    ASK_BEST = "ASK_BEST"
    AT_TRADE = "AT_TRADE"
    AT_BID = "AT_BID"
    AT_ASK = "AT_ASK"