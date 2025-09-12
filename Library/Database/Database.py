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

    SCHEMA_MARKET: dict = {
        Bar.Timestamp: pl.Datetime(),
        Bar.OpenPrice: pl.Float32(),
        Bar.HighPrice: pl.Float32(),
        Bar.LowPrice: pl.Float32(),
        Bar.ClosePrice: pl.Float32(),
        Bar.TickVolume: pl.Float32()
    }

    SCHEMA_SYMBOL: dict = {
        Symbol.BaseAssetType: pl.Enum([currency.name for currency in AssetType]),
        Symbol.QuoteAssetType: pl.Enum([currency.name for currency in AssetType]),
        Symbol.Digits: pl.Int8(),
        Symbol.PointSize: pl.Float32(),
        Symbol.PipSize: pl.Float32(),
        Symbol.LotSize: pl.Float32(),
        Symbol.VolumeInUnitsMin: pl.Float32(),
        Symbol.VolumeInUnitsMax: pl.Float32(),
        Symbol.VolumeInUnitsStep: pl.Float32(),
        Symbol.Commission: pl.Float32(),
        Symbol.CommissionMode: pl.Enum([commission.name for commission in CommissionMode]),
        Symbol.SwapLong: pl.Float32(),
        Symbol.SwapShort: pl.Float32(),
        Symbol.SwapMode: pl.Enum([swap.name for swap in SwapMode]),
        Symbol.SwapExtraDay: pl.Enum([day.name for day in DayOfWeek]),
        Symbol.SwapSummerTime: pl.Int8(),
        Symbol.SwapWinterTime: pl.Int8(),
        Symbol.SwapPeriod: pl.Int8()
    }

    SCHEMA_TRADE: dict = {
        Trade.PositionID: pl.Int32(),
        Trade.TradeID: pl.Int32(),
        Trade.PositionType: pl.Enum([pos_type.name for pos_type in PositionType]),
        Trade.TradeType: pl.Enum([trade_type.name for trade_type in TradeType]),
        Trade.EntryTimestamp: pl.Datetime(),
        Trade.ExitTimestamp: pl.Datetime(),
        Trade.EntryPrice: pl.Float32(),
        Trade.ExitPrice: pl.Float32(),
        Trade.Volume: pl.Float32(),
        Trade.Quantity: pl.Float32(),
        Trade.Points: pl.Float32(),
        Trade.Pips: pl.Float32(),
        Trade.GrossPnL: pl.Float32(),
        Trade.CommissionPnL: pl.Float32(),
        Trade.SwapPnL: pl.Float32(),
        Trade.NetPnL: pl.Float32(),
        Trade.DrawdownPoints: pl.Float32(),
        Trade.DrawdownPips: pl.Float32(),
        Trade.DrawdownPnL: pl.Float32(),
        Trade.DrawdownReturn: pl.Float32(),
        Trade.NetReturn: pl.Float32(),
        Trade.NetLogReturn: pl.Float32(),
        Trade.NetReturnDrawdown: pl.Float32(),
        Trade.BaseBalance: pl.Float32(),
        Trade.EntryBalance: pl.Float32(),
        Trade.ExitBalance: pl.Float32(),
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
            market_data = [bar.dict() for bar in market_data]
        elif isinstance(market_data, Bar):
            market_data = [market_data.dict()]
        else:
            market_data = None
        return pl.DataFrame(data=market_data, schema=cls.SCHEMA_MARKET, orient="row")
    
    @classmethod
    def format_symbol_data(cls, symbol_data: pl.DataFrame | List[Symbol] | Symbol | None) -> pl.DataFrame:
        if isinstance(symbol_data, pl.DataFrame) and symbol_data.schema == cls.SCHEMA_SYMBOL:
            return symbol_data
        if isinstance(symbol_data, list):
            symbol_data = [symbol.dict() for symbol in symbol_data]
        elif isinstance(symbol_data, Symbol):
            symbol_data = [symbol_data.dict()]
        else:
            symbol_data = None
        return pl.DataFrame(data=symbol_data, schema=cls.SCHEMA_SYMBOL, orient="row")
    
    @classmethod
    def format_trade_data(cls, trade_data: pl.DataFrame | List[Trade] | Trade | None) -> pl.DataFrame:
        if isinstance(trade_data, pl.DataFrame) and trade_data.schema == cls.SCHEMA_TRADE:
            return trade_data
        if isinstance(trade_data, list):
            trade_data = [trade.dict() for trade in trade_data]
        elif isinstance(trade_data, Trade):
            trade_data = [trade_data.dict()]
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
                INSERT INTO "{self._symbol}"."{self._timeframe}" ("{Bar.Timestamp}", "{Bar.OpenPrice}", "{Bar.HighPrice}", "{Bar.LowPrice}", "{Bar.ClosePrice}", "{Bar.TickVolume}")
                VALUES %s
                ON CONFLICT ("{Bar.Timestamp}") DO UPDATE SET
                    "{Bar.OpenPrice}" = EXCLUDED."{Bar.OpenPrice}",
                    "{Bar.HighPrice}" = EXCLUDED."{Bar.HighPrice}",
                    "{Bar.LowPrice}" = EXCLUDED."{Bar.LowPrice}",
                    "{Bar.ClosePrice}" = EXCLUDED."{Bar.ClosePrice}",
                    "{Bar.TickVolume}" = EXCLUDED."{Bar.TickVolume}"
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
                    "{Symbol.BaseAssetType}" = %s,
                    "{Symbol.QuoteAssetType}" = %s,
                    "{Symbol.Digits}" = %s,
                    "{Symbol.PointSize}" = %s,
                    "{Symbol.PipSize}" = %s,
                    "{Symbol.LotSize}" = %s,
                    "{Symbol.VolumeInUnitsMin}" = %s,
                    "{Symbol.VolumeInUnitsMax}" = %s,
                    "{Symbol.VolumeInUnitsStep}" = %s,
                    "{Symbol.Commission}" = %s,
                    "{Symbol.CommissionMode}" = %s,
                    "{Symbol.SwapLong}" = %s,
                    "{Symbol.SwapShort}" = %s,
                    "{Symbol.SwapMode}" = %s,
                    "{Symbol.SwapExtraDay}" = %s,
                    "{Symbol.SwapSummerTime}" = %s,
                    "{Symbol.SwapWinterTime}" = %s,
                    "{Symbol.SwapPeriod}" = %s;
                """

                cursor.execute(query, symbol.tuple())
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
            start_condition = f'"{Bar.Timestamp}" >= %s'


            if window is not None and window > 0:
                try:
                    with self._connection.cursor() as cursor:
                        window_query = f"""
                        SELECT "{Bar.Timestamp}" 
                        FROM {table_name} 
                        WHERE "{Bar.Timestamp}" < %s
                        ORDER BY "{Bar.Timestamp}" DESC
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
            stop_condition = f'"{Bar.Timestamp}" <= %s'
            params.append(stop)
            conditions.append(stop_condition)

        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += f' ORDER BY "{Bar.Timestamp}"'

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                bars = [Bar(
                    Timestamp=result[0],
                    OpenPrice=result[1],
                    HighPrice=result[2],
                    LowPrice=result[3],
                    ClosePrice=result[4],
                    TickVolume=result[5]) for result in results]
                data = self.format_market_data(bars)
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
                    PointSize=result[3],
                    PipSize=result[4],
                    LotSize=result[5],
                    VolumeInUnitsMin=result[6],
                    VolumeInUnitsMax=result[7],
                    VolumeInUnitsStep=result[8],
                    Commission=result[9],
                    CommissionMode=CommissionMode(CommissionMode[result[10]]),
                    SwapLong=result[11],
                    SwapShort=result[12],
                    SwapMode=SwapMode(SwapMode[result[13]]),
                    SwapExtraDay=DayOfWeek(DayOfWeek[result[14]]),
                    SwapSummerTime=result[15],
                    SwapWinterTime=result[16],
                    SwapPeriod=result[17],
                )
        except Exception as e:
            self._log.error(lambda: str(e))
            raise e

    def generate_market_data(self):
        raise NotImplemented
