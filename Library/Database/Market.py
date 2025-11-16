from Library.Database import PostgresAPI, QueryAPI
from Library.Utility import PathAPI

class MarketDatabaseAPI(PostgresAPI):

    def __init__(self,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str):

        super().__init__(
            database=broker,
            schema=symbol,
            table=timeframe
        )

        self.broker = broker
        self.group = group
        self.symbol = symbol
        self.timeframe = timeframe

    def _database_(self):
        query = QueryAPI(PathAPI("Check/Database.sql"))
        self.execute(query)
        result = self.fetchall()
        self.commit()
        if not result.is_empty(): return
        query = QueryAPI(PathAPI("Create/Database.sql"))
        self.execute(query)
        self.commit()

    def _schema_(self):
        query = QueryAPI(PathAPI("Check/Schema.sql"))
        self.execute(query)
        result = self.fetchall()
        if not result.is_empty(): return
        query = QueryAPI(PathAPI("Create/Schema.sql"))
        self.execute(query)
        self.commit()

    def _table_(self):
        pass
