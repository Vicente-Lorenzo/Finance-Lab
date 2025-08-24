import hashlib
import polars as pl
import psycopg2 as pg
import psycopg2.extras as pge

from typing import List

from Library.Classes import *
from Library.Logging import HandlerAPI
from Library.Utils import timer

class DatabaseAPI:

    HOST = "localhost"
    PORT = 5432
    
    MARKET_TIMESTAMP = "Timestamp"
    MARKET_OPENPRICE = "OpenPrice"
    MARKET_HIGHPRICE = "HighPrice"
    MARKET_LOWPRICE = "LowPrice"
    MARKET_CLOSEPRICE = "ClosePrice"
    MARKET_TICKVOLUME = "TickVolume"

    SYMBOL_BASEASSET = "BaseAsset"
    SYMBOL_QUOTEASSET = "QuoteAsset"
    SYMBOL_DIGITS = "Digits"
    SYMBOL_POINTSIZE = "PointSize"
    SYMBOL_PIPSIZE = "PipSize"
    SYMBOL_LOTSIZE = "LotSize"
    SYMBOL_VOLUMEINUNITSMIN = "VolumeInUnitsMin"
    SYMBOL_VOLUMEINUNITSMAX = "VolumeInUnitsMax"
    SYMBOL_VOLUMEINUNITSSTEP = "VolumeInUnitsStep"
    SYMBOL_COMMISSION = "Commission"
    SYMBOL_COMMISSIONMODE = "CommissionType"
    SYMBOL_SWAPLONG = "SwapLong"
    SYMBOL_SWAPSHORT = "SwapShort"
    SYMBOL_SWAPMODE = "SwapCalculationType"
    SYMBOL_SWAPEXTRADAY = "Swap3DaysRollover"
    SYMBOL_SWAPTIME = "SwapTime"
    SYMBOL_SWAPPERIOD = "SwapPeriod"

    TRADE_POSITIONID = "PositionID"
    TRADE_TRADEID = "TradeID"
    TRADE_POSITIONTYPE = "PositionType"
    TRADE_TRADETYPE = "TradeType"
    TRADE_ENTRYTIMESTAMP = "EntryTimestamp"
    TRADE_EXITTIMESTAMP = "ExitTimestamp"
    TRADE_ENTRYPRICE = "EntryPrice"
    TRADE_EXITPRICE = "ExitPrice"
    TRADE_VOLUME = "Volume"
    TRADE_QUANTITY = "Quantity"
    TRADE_POINTS = "Points"
    TRADE_PIPS = "Pips"
    TRADE_GROSSPNL = "GrossPnL"
    TRADE_COMMISSIONPNL = "CommissionPnL"
    TRADE_SWAPPNL = "SwapPnL"
    TRADE_NETPNL = "NetPnL"
    TRADE_DRAWDOWNPOINTS = "DrawdownPoints"
    TRADE_DRAWDOWNPIPS = "DrawdownPips"
    TRADE_DRAWDOWNPNL = "DrawdownPnL"
    TRADE_DRAWDOWNRETURN = "DrawdownReturn"
    TRADE_NETRETURN = "NetReturn"
    TRADE_NETLOGRETURN = "NetLogReturn"
    TRADE_NETRETURNDRAWDOWN = "NetReturnDrawdown"
    TRADE_BASEBALANCE = "BaseBalance"
    TRADE_ENTRYBALANCE = "EntryBalance"
    TRADE_EXITBALANCE = "ExitBalance"

    SCHEMA_MARKET: dict = {
        MARKET_TIMESTAMP: pl.Datetime(),
        MARKET_OPENPRICE: pl.Float32(),
        MARKET_HIGHPRICE: pl.Float32(),
        MARKET_LOWPRICE: pl.Float32(),
        MARKET_CLOSEPRICE: pl.Float32(),
        MARKET_TICKVOLUME: pl.Float32()
    }

    SCHEMA_SYMBOL: dict = {
        SYMBOL_BASEASSET: pl.Enum([currency.name for currency in AssetType]),
        SYMBOL_QUOTEASSET: pl.Enum([currency.name for currency in AssetType]),
        SYMBOL_DIGITS: pl.Int8(),
        SYMBOL_POINTSIZE: pl.Float32(),
        SYMBOL_PIPSIZE: pl.Float32(),
        SYMBOL_LOTSIZE: pl.Float32(),
        SYMBOL_VOLUMEINUNITSMIN: pl.Float32(),
        SYMBOL_VOLUMEINUNITSMAX: pl.Float32(),
        SYMBOL_VOLUMEINUNITSSTEP: pl.Float32(),
        SYMBOL_COMMISSION: pl.Float32(),
        SYMBOL_COMMISSIONMODE: pl.Enum([commission.name for commission in CommissionMode]),
        SYMBOL_SWAPLONG: pl.Float32(),
        SYMBOL_SWAPSHORT: pl.Float32(),
        SYMBOL_SWAPMODE: pl.Enum([swap.name for swap in SwapMode]),
        SYMBOL_SWAPEXTRADAY: pl.Enum([day.name for day in DayOfWeek])
    }

    SCHEMA_TRADE: dict = {
        TRADE_POSITIONID: pl.Int32(),
        TRADE_TRADEID: pl.Int32(),
        TRADE_POSITIONTYPE: pl.Enum([pos_type.name for pos_type in PositionType]),
        TRADE_TRADETYPE: pl.Enum([trade_type.name for trade_type in TradeType]),
        TRADE_ENTRYTIMESTAMP: pl.Datetime(),
        TRADE_EXITTIMESTAMP: pl.Datetime(),
        TRADE_ENTRYPRICE: pl.Float32(),
        TRADE_EXITPRICE: pl.Float32(),
        TRADE_VOLUME: pl.Float32(),
        TRADE_QUANTITY: pl.Float32(),
        TRADE_POINTS: pl.Float32(),
        TRADE_PIPS: pl.Float32(),
        TRADE_GROSSPNL: pl.Float32(),
        TRADE_COMMISSIONPNL: pl.Float32(),
        TRADE_SWAPPNL: pl.Float32(),
        TRADE_NETPNL: pl.Float32(),
        TRADE_DRAWDOWNPOINTS: pl.Float32(),
        TRADE_DRAWDOWNPIPS: pl.Float32(),
        TRADE_DRAWDOWNPNL: pl.Float32(),
        TRADE_DRAWDOWNRETURN: pl.Float32(),
        TRADE_NETRETURN: pl.Float32(),
        TRADE_NETLOGRETURN: pl.Float32(),
        TRADE_NETRETURNDRAWDOWN: pl.Float32(),
        TRADE_BASEBALANCE: pl.Float32(),
        TRADE_ENTRYBALANCE: pl.Float32(),
        TRADE_EXITBALANCE: pl.Float32(),
    }

    def __init__(self,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str):
        self._broker: str = broker
        self._group: str = group
        self._symbol: str = symbol
        self._timeframe: str = timeframe

        self._user: str = self._generate_user(broker, symbol, timeframe)
        self._password: str = self._generate_password(self._user)
        self._connection = None

        self._log: HandlerAPI = HandlerAPI(
            Broker=broker,
            Group=group,
            Symbol=symbol,
            Timeframe=timeframe,
            Class=self.__class__.__name__,
            Subclass="Database Management"
        )

    @staticmethod
    def _generate_user(broker: str, symbol: str, timeframe: str) -> str:
        return f"{broker}_{symbol}_{timeframe}_User"

    @staticmethod
    def _generate_password(user: str) -> str:
        return hashlib.sha256(user.encode()).hexdigest()

    def __enter__(self):
        try:
            self._connection = pg.connect(
                host=self.HOST,
                port=self.PORT,
                dbname=self._broker,
                user=self._user,
                password=self._password
            )
            self._log.debug(lambda: "Connected")
        except Exception as e:
            self._log.error(lambda: str(e))
            raise e
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._connection:
            self._connection.close()
        if exc_type or exc_value or exc_traceback:
            self._log.exception(lambda: f"Exception type: {exc_type}")
            self._log.exception(lambda: f"Exception value: {exc_value}")
            self._log.exception(lambda: f"Traceback: {exc_traceback}")
        self._log.debug(lambda: "Disconnected")
        return self

    @classmethod
    def format_market_data(cls, market_data: pl.DataFrame | List[Bar] | Bar | None) -> pl.DataFrame:
        if isinstance(market_data, pl.DataFrame) and market_data.schema == cls.SCHEMA_MARKET:
            return market_data
        if isinstance(market_data, list):
            market_data = [astuple(bar) for bar in market_data]
        elif isinstance(market_data, Bar):
            market_data = [astuple(market_data)]
        else:
            market_data = None
        return pl.DataFrame(data=market_data, schema=cls.SCHEMA_MARKET, orient="row")
    
    @classmethod
    def format_symbol_data(cls, symbol_data: pl.DataFrame | List[Symbol] | Symbol | None) -> pl.DataFrame:
        if isinstance(symbol_data, pl.DataFrame) and symbol_data.schema == cls.SCHEMA_SYMBOL:
            return symbol_data
        if isinstance(symbol_data, list):
            symbol_data = [astuple(symbol) for symbol in symbol_data]
        elif isinstance(symbol_data, Symbol):
            symbol_data = [astuple(symbol_data)]
        else:
            symbol_data = None
        return pl.DataFrame(data=symbol_data, schema=cls.SCHEMA_SYMBOL, orient="row")
    
    @classmethod
    def format_trade_data(cls, trade_data: pl.DataFrame | List[Trade] | Trade | None) -> pl.DataFrame:
        if isinstance(trade_data, pl.DataFrame) and trade_data.schema == cls.SCHEMA_TRADE:
            return trade_data
        if isinstance(trade_data, list):
            trade_data = [astuple(trade) for trade in trade_data]
        elif isinstance(trade_data, Trade):
            trade_data = [astuple(trade_data)]
        else:
            trade_data = None
        return pl.DataFrame(data=trade_data, schema=cls.SCHEMA_TRADE, orient="row")

    @timer
    def push_market_data(self, data: pl.DataFrame) -> None:
        if not self._connection:
            self._log.error(lambda: "Connection is not established")
            raise

        try:
            with self._connection.cursor() as cursor:
                records = [tuple(row) for row in data.rows()]

                query = f"""
                INSERT INTO "{self._symbol}"."{self._timeframe}" ("{DatabaseAPI.MARKET_TIMESTAMP}", "{DatabaseAPI.MARKET_OPENPRICE}", "{DatabaseAPI.MARKET_HIGHPRICE}", "{DatabaseAPI.MARKET_LOWPRICE}", "{DatabaseAPI.MARKET_CLOSEPRICE}", "{DatabaseAPI.MARKET_TICKVOLUME}")
                VALUES %s
                ON CONFLICT ("{DatabaseAPI.MARKET_TIMESTAMP}") DO UPDATE SET
                    "{DatabaseAPI.MARKET_OPENPRICE}" = EXCLUDED."{DatabaseAPI.MARKET_OPENPRICE}",
                    "{DatabaseAPI.MARKET_HIGHPRICE}" = EXCLUDED."{DatabaseAPI.MARKET_HIGHPRICE}",
                    "{DatabaseAPI.MARKET_LOWPRICE}" = EXCLUDED."{DatabaseAPI.MARKET_LOWPRICE}",
                    "{DatabaseAPI.MARKET_CLOSEPRICE}" = EXCLUDED."{DatabaseAPI.MARKET_CLOSEPRICE}",
                    "{DatabaseAPI.MARKET_TICKVOLUME}" = EXCLUDED."{DatabaseAPI.MARKET_TICKVOLUME}";
                """

                pge.execute_values(cursor, query, records)
                self._connection.commit()
                self._log.debug(lambda: f"Saved {len(data)} market data points")
        except Exception as e:
            self._connection.rollback()
            self._log.error(lambda: str(e))
            raise e

    @timer
    def push_symbol_data(self, symbol: Symbol) -> None:
        if not self._connection:
            self._log.error(lambda: "Connection is not established")
            raise

        try:
            with self._connection.cursor() as cursor:
                
                query = f"""
                UPDATE "{self._symbol}"."Symbol" SET 
                    "{DatabaseAPI.SYMBOL_BASEASSET}" = %s,
                    "{DatabaseAPI.SYMBOL_QUOTEASSET}" = %s,
                    "{DatabaseAPI.SYMBOL_DIGITS}" = %s,
                    "{DatabaseAPI.SYMBOL_POINTSIZE}" = %s,
                    "{DatabaseAPI.SYMBOL_PIPSIZE}" = %s,
                    "{DatabaseAPI.SYMBOL_LOTSIZE}" = %s,
                    "{DatabaseAPI.SYMBOL_VOLUMEINUNITSMIN}" = %s,
                    "{DatabaseAPI.SYMBOL_VOLUMEINUNITSMAX}" = %s,
                    "{DatabaseAPI.SYMBOL_VOLUMEINUNITSSTEP}" = %s,
                    "{DatabaseAPI.SYMBOL_COMMISSION}" = %s,
                    "{DatabaseAPI.SYMBOL_COMMISSIONMODE}" = %s,
                    "{DatabaseAPI.SYMBOL_SWAPLONG}" = %s,
                    "{DatabaseAPI.SYMBOL_SWAPSHORT}" = %s,
                    "{DatabaseAPI.SYMBOL_SWAPMODE}" = %s,
                    "{DatabaseAPI.SYMBOL_SWAPEXTRADAY}" = %s,
                    "{DatabaseAPI.SYMBOL_SWAPTIME}" = %s,
                    "{DatabaseAPI.SYMBOL_SWAPPERIOD}" = %s;
                """

                cursor.execute(query, astuple(symbol))
                self._connection.commit()
                self._log.debug(lambda: f"Saved symbol data points")
        except Exception as e:
            self._connection.rollback()
            self._log.error(lambda: str(e))
            raise e

    @timer
    def pull_market_data(self, start: str | None = None, stop: str | None = None, window: int | None = None) -> pl.DataFrame | None:
        if not self._connection:
            self._log.error(lambda: "Connection is not established")
            raise

        table_name = f'"{self._symbol}"."{self._timeframe}"'
        params = []
        conditions = []

        if start is not None:
            start_condition = f'"{DatabaseAPI.MARKET_TIMESTAMP}" >= %s'


            if window is not None and window > 0:
                try:
                    with self._connection.cursor() as cursor:
                        window_query = f"""
                        SELECT "{DatabaseAPI.MARKET_TIMESTAMP}" 
                        FROM {table_name} 
                        WHERE "{DatabaseAPI.MARKET_TIMESTAMP}" < %s
                        ORDER BY "{DatabaseAPI.MARKET_TIMESTAMP}" DESC
                        LIMIT %s;
                        """
                        cursor.execute(window_query, (start, window))
                        preceding_rows = cursor.fetchall()
                        if preceding_rows:
                            first_window_timestamp = preceding_rows[-1][0]
                            start = first_window_timestamp
                except Exception as e:
                    self._log.error(lambda: str(e))
                    raise e

            params.append(start)
            conditions.append(start_condition)

        if stop is not None:
            stop_condition = f'"{DatabaseAPI.MARKET_TIMESTAMP}" <= %s'
            params.append(stop)
            conditions.append(stop_condition)

        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += f' ORDER BY "{DatabaseAPI.MARKET_TIMESTAMP}"'

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                results = [Bar(*result) for result in results]
                data = self.format_market_data(results)
                self._log.debug(lambda: f"Loaded {len(data)} data points")
                return data
        except Exception as e:
            self._log.error(lambda: str(e))
            raise e

    @timer
    def pull_symbol_data(self) -> Symbol | None:
        if not self._connection:
            self._log.error(lambda: "Connection is not established")
            raise

        query = f'SELECT * FROM "{self._symbol}"."Symbol"'

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                self._log.debug(lambda: f"Loaded symbol data points")
                
                return Symbol(
                    BaseAssetType=AssetType(AssetType[result[0]]),
                    QuoteAssetType=AssetType(AssetType[result[1]]),
                    Digits=result[2],
                    PointSize=result[4],
                    PipSize=result[3],
                    LotSize=result[5],
                    VolumeInUnitsMin=result[6],
                    VolumeInUnitsMax=result[7],
                    VolumeInUnitsStep=result[8],
                    Commission=result[9],
                    CommissionMode=CommissionMode(CommissionMode[result[10]]),
                    SwapLong=result[11],
                    SwapShort=result[12],
                    SwapMode=SwapMode(SwapMode[result[13]]),
                    SwapExtraDay=DayOfWeek(DayOfWeek[result[14]])
                )
        except Exception as e:
            self._log.error(lambda: str(e))
            raise e

    def generate_market_data(self):
        raise NotImplemented
