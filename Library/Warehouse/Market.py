from Library.Logging import HandlerAPI
from Library.Warehouse import *

class MarketWarehouseAPI:

    def __init__(self,
                 broker: str,
                 symbol: str | list[str],
                 timeframe: str | list[str]):

        self.broker = broker
        self.symbol = symbol
        self.timeframe = timeframe

        self._log_ = HandlerAPI(
            Broker=self.broker,
            Symbol=self.symbol,
            Timeframe=self.timeframe,
            Class=self.__class__.__name__
        )

        self.Symbol = SymbolDatabaseAPI(
            database=broker,
            schema=symbol,
            table="Symbol"
        )

        self.Tick = TickDatabaseAPI(
            database=broker,
            schema=symbol,
            table="Tick"
        )

        self.Bar = SymbolDatabaseAPI(
            database=broker,
            schema=symbol,
            table=timeframe
        )

        self.Trade = TradeDatabaseAPI(
            database=broker,
            schema=symbol,
            table="Trade"
        )

    def __enter__(self):
        self.Symbol.__enter__()
        self.Tick.__enter__()
        self.Bar.__enter__()
        self.Trade.__enter__()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.Symbol.__exit__(exception_type, exception_value, exception_traceback)
        self.Tick.__exit__(exception_type, exception_value, exception_traceback)
        self.Bar.__exit__(exception_type, exception_value, exception_traceback)
        self.Trade.__exit__(exception_type, exception_value, exception_traceback)
        if exception_type or exception_value or exception_traceback:
            self._log_.exception(lambda: f"Exception type: {exception_type}")
            self._log_.exception(lambda: f"Exception value: {exception_value}")
            self._log_.exception(lambda: f"Traceback: {exception_traceback}")
            return False
        else:
            return True
