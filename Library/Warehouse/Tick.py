from Library.DataFrame import pl
from Library.Dataclass import *
from Library.Database import PostgresAPI

class TickDatabaseAPI(PostgresAPI):

    _STRUCTURE_: dict = {
        TickAPI.ID.Timestamp.DateTime: pl.Datetime(),
        TickAPI.ID.Ask.Price: pl.Float64(),
        TickAPI.ID.Bid.Price: pl.Float64(),
        TickAPI.ID.AskBaseConversion: pl.Float64(),
        TickAPI.ID.BidBaseConversion: pl.Float64(),
        TickAPI.ID.AskQuoteConversion: pl.Float64(),
        TickAPI.ID.BidQuoteConversion: pl.Float64()
    }
