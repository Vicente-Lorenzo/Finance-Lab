import math
import polars as pl

from datetime import datetime, timedelta

from Library.Robots.Database.Database import DatabaseAPI
from Library.Robots.Container.Enums import TradeType
from Library.Robots.Container.Classes import Account, Trade

class StatisticsAPI:
    
    STATISTICS_METRICS_LABEL = "Statistical Metrics"
    BUY_METRICS_INDIVIDUAL = "Buy Metrics (Individual)"
    SELL_METRICS_INDIVIDUAL = "Sell Metrics (Individual)"
    TOTAL_METRICS_INDIVIDUAL = "Total Metrics (Individual)"
    BUY_METRICS_AGGREGATED = "Buy Metrics (Aggregated)"
    SELL_METRICS_AGGREGATED = "Sell Metrics (Aggregated)"
    TOTAL_METRICS_AGGREGATED = "Total Metrics (Aggregated)"

    NUMBEROFTRADES = "Nr of Trades"
    
    NUMBEROFWINNINGTRADES = "Nr of Winning Trades"
    WINNINGRATEPERC = "Winning Rate (%)"
    MAXWINNINGTRADE = "Max Winning Trade (€)"
    AVERAGEWINNINGTRADE = "Avg Winning Trade (€)"
    MINWINNINGTRADE = "Min Winning Trade (€)"
    MAXWINNINGPIPS = "Max Winning Pips"
    AVERAGEWINNINGPIPS = "Avg Winning Pips"
    MINWINNINGPIPS = "Min Winning Pips"
    MAXWINNINGSTREAK = "Max Winning Streak"
    EXPECTEDWINNINGRETURNPERC = "Expected Winning Return (%)"
    WINNINGRETURNPERC = "Winning Return (%)"
    WINNINGRETURNANNPERC = "Winning Return Annualised (%) [µ_up]"
    WINNINGVOLATILITYPERC = "Winning Volatility (%)"
    WINNINGVOLATILITYANNPERC = "Winning Volatility Annualised (%) [σ_up]"
    
    NUMBEROFLOSINGTRADES = "Nr of Losing Trades"
    LOSINGRATEPERC = "Losing Rate (%)"
    MAXLOSINGTRADE = "Max Losing Trade (€)"
    AVERAGELOSINGTRADE = "Avg Losing Trade (€)"
    MINLOSINGTRADE = "Min Losing Trade (€)"
    MAXLOSINGPIPS = "Max Losing Pips"
    AVERAGELOSINGPIPS = "Avg Losing Pips"
    MINLOSINGPIPS = "Min Losing Pips"
    MAXLOSINGSTREAK = "Max Losing Streak"
    EXPECTEDLOSINGRETURNPERC = "Expected Losing Return (%)"
    LOSINGRETURNPERC = "Losing Return (%)"
    LOSINGRETURNANNPERC = "Losing Return Annualised (%) [µ_down]"
    LOSINGVOLATILITYPERC = "Losing Volatility (%)"
    LOSINGVOLATILITYANNPERC = "Losing Volatility Annualised (%) [σ_down]"
    
    AVERAGETRADE = "Average Trade (€) [Backward]"
    AVERAGEPIPS = "Average Pips [Backward]"
    EXPECTEDTRADE = "Expected Trade (€) [Forward]"
    EXPECTEDPIPS = "Expected Pips [Forward]"
    
    GROSSPNLVALUE = "Gross Profit/Loss (€)"
    COMMISSIONSPNLVALUE = "Commissions Profit/Loss (€)"
    SWAPSPNLVALUE = "Swaps Profit/Loss (€)"
    NETPNLVALUE = "Net Profit/Loss (€)"
    EXPECTEDNETRETURNPERC = "Expected Net Return (%)"
    NETRETURNPERC = "Net Return (%)"
    NETRETURNANNPERC = "Net Return Annualised (%) [µ]"
    NETVOLATILITYPERC = "Net Volatility (%)"
    NETVOLATILITYANNPERC = "Net Volatility Annualised (%) [σ]"
    NETPIPSVALUE = "Net Pips"

    PROFITFACTOR = "Profit Factor"
    RISKTOREWARDRATIO = "Risk-to-Reward Ratio"
    MAXDRAWDOWNVALUE = "Max Drawdown (€)"
    MAXDRAWDOWNPERC = "Max Drawdown (%)"
    MEANDRAWDOWNVALUE = "Mean Drawdown (€)"
    MEANDRAWDOWNPERC = "Mean Drawdown (%)"
    MAXHOLDINGTIME = "Max Holding Time (Days)"
    AVERAGEHOLDINGTIME = "Avg Holding Time (Days)"
    MINHOLDINGTIME = "Min Holding Time (Days)"
    SHARPERATIO = "Sharpe Ratio"
    SORTINORATIO = "Sortino Ratio"
    CALMARRATIO = "Calmar Ratio"
    FITNESSRATIO = "Fitness Ratio"
    
    Metrics = [
        NUMBEROFTRADES,

        NUMBEROFWINNINGTRADES,
        WINNINGRATEPERC,
        MAXWINNINGTRADE,
        AVERAGEWINNINGTRADE,
        MINWINNINGTRADE,
        MAXWINNINGPIPS,
        AVERAGEWINNINGPIPS,
        MINWINNINGPIPS,
        MAXWINNINGSTREAK,
        EXPECTEDWINNINGRETURNPERC,
        WINNINGRETURNPERC,
        WINNINGRETURNANNPERC,
        WINNINGVOLATILITYPERC,
        WINNINGVOLATILITYANNPERC,
    
        NUMBEROFLOSINGTRADES,
        LOSINGRATEPERC,
        MAXLOSINGTRADE,
        AVERAGELOSINGTRADE,
        MINLOSINGTRADE,
        MAXLOSINGPIPS,
        AVERAGELOSINGPIPS,
        MINLOSINGPIPS,
        MAXLOSINGSTREAK,
        EXPECTEDLOSINGRETURNPERC,
        LOSINGRETURNPERC,
        LOSINGRETURNANNPERC,
        LOSINGVOLATILITYPERC,
        LOSINGVOLATILITYANNPERC,
    
        AVERAGETRADE,
        AVERAGEPIPS,
        EXPECTEDTRADE,
        EXPECTEDPIPS,
    
        GROSSPNLVALUE,
        COMMISSIONSPNLVALUE,
        SWAPSPNLVALUE,
        NETPNLVALUE,
        EXPECTEDNETRETURNPERC,
        NETRETURNPERC,
        NETRETURNANNPERC,
        NETVOLATILITYPERC,
        NETVOLATILITYANNPERC,
        NETPIPSVALUE,
    
        PROFITFACTOR,
        RISKTOREWARDRATIO,
        MAXDRAWDOWNVALUE,
        MAXDRAWDOWNPERC,
        MEANDRAWDOWNVALUE,
        MEANDRAWDOWNPERC,
        MAXHOLDINGTIME,
        AVERAGEHOLDINGTIME,
        MINHOLDINGTIME,
        SHARPERATIO,
        SORTINORATIO,
        CALMARRATIO,
        FITNESSRATIO
    ]
    
    EPSILON = 1e-2
    
    def __init__(self):
        self._data : pl.DataFrame = DatabaseAPI.format_trade_data(None)        

    def update_data(self, trade: Trade) -> None:
        self._data.extend(DatabaseAPI.format_trade_data(trade))

    @staticmethod
    def sort_trades(trades_df: pl.DataFrame) -> pl.DataFrame:
        return trades_df.sort(by=DatabaseAPI.TRADE_EXITTIMESTAMP, descending=False)

    @staticmethod
    def aggregate_trades(trades_df: pl.DataFrame) -> pl.DataFrame:
        return trades_df.group_by(DatabaseAPI.TRADE_POSITIONID).agg([
            pl.col(DatabaseAPI.TRADE_TRADEID),
            pl.col(DatabaseAPI.TRADE_POSITIONTYPE).first().alias(DatabaseAPI.TRADE_POSITIONTYPE),
            pl.col(DatabaseAPI.TRADE_TRADETYPE).first().alias(DatabaseAPI.TRADE_TRADETYPE),
            pl.col(DatabaseAPI.TRADE_ENTRYTIMESTAMP).min().alias(DatabaseAPI.TRADE_ENTRYTIMESTAMP),
            pl.col(DatabaseAPI.TRADE_EXITTIMESTAMP).max().alias(DatabaseAPI.TRADE_EXITTIMESTAMP),
            pl.col(DatabaseAPI.TRADE_ENTRYPRICE).first().alias(DatabaseAPI.TRADE_ENTRYPRICE),
            pl.col(DatabaseAPI.TRADE_EXITPRICE).last().alias(DatabaseAPI.TRADE_EXITPRICE),
            pl.col(DatabaseAPI.TRADE_VOLUME).sum().alias(DatabaseAPI.TRADE_VOLUME),
            pl.col(DatabaseAPI.TRADE_GROSSPNL).sum().alias(DatabaseAPI.TRADE_GROSSPNL),
            pl.col(DatabaseAPI.TRADE_COMMISSIONPNL).sum().alias(DatabaseAPI.TRADE_COMMISSIONPNL),
            pl.col(DatabaseAPI.TRADE_SWAPPNL).sum().alias(DatabaseAPI.TRADE_SWAPPNL),
            pl.col(DatabaseAPI.TRADE_NETPIPS).sum().alias(DatabaseAPI.TRADE_NETPIPS),
            pl.col(DatabaseAPI.TRADE_NETPNL).sum().alias(DatabaseAPI.TRADE_NETPNL),
            pl.col(DatabaseAPI.TRADE_DRAWDOWNPIPS).min().alias(DatabaseAPI.TRADE_DRAWDOWNPIPS),
            pl.col(DatabaseAPI.TRADE_DRAWDOWNPNL).min().alias(DatabaseAPI.TRADE_DRAWDOWNPNL),
            pl.col(DatabaseAPI.TRADE_DRAWDOWNRETURN).min().alias(DatabaseAPI.TRADE_DRAWDOWNRETURN),
            pl.col(DatabaseAPI.TRADE_NETRETURN).sum().alias(DatabaseAPI.TRADE_NETRETURN),
            pl.col(DatabaseAPI.TRADE_NETLOGRETURN).sum().alias(DatabaseAPI.TRADE_NETLOGRETURN),
            pl.col(DatabaseAPI.TRADE_NETRETURNDRAWDOWN).sum().alias(DatabaseAPI.TRADE_NETRETURNDRAWDOWN),
            pl.col(DatabaseAPI.TRADE_BASEBALANCE).first().alias(DatabaseAPI.TRADE_BASEBALANCE),
            pl.col(DatabaseAPI.TRADE_ENTRYBALANCE).first().alias(DatabaseAPI.TRADE_ENTRYBALANCE),
            pl.col(DatabaseAPI.TRADE_EXITBALANCE).last().alias(DatabaseAPI.TRADE_EXITBALANCE),
        ])

    @staticmethod
    def split_buy_sell_trades(trades_df: pl.DataFrame) -> (pl.DataFrame, pl.DataFrame):
        return (trades_df.filter(pl.col(DatabaseAPI.TRADE_TRADETYPE) == TradeType.Buy.name),
                trades_df.filter(pl.col(DatabaseAPI.TRADE_TRADETYPE) == TradeType.Sell.name))
    
    @staticmethod
    def split_winning_losing_trades(trades_df: pl.DataFrame) -> (pl.DataFrame, pl.DataFrame):
        return (trades_df.filter(pl.col(DatabaseAPI.TRADE_NETPNL) > 0),
                trades_df.filter(pl.col(DatabaseAPI.TRADE_NETPNL) <= 0))

    @staticmethod
    def calculate_total_trades(trades_df: pl.DataFrame) -> int:
        return trades_df.shape[0]
    
    @staticmethod
    def calculate_rate_perc(nr_cases: int, nr_trades: int) -> float:
        return (nr_cases / nr_trades) * 100 if nr_trades else 0.0
    
    @staticmethod
    def calculate_min_avg_max(nr_trades: int, trades_df: pl.DataFrame, column) -> (float, float, float):
        if nr_trades > 0:
            max_value = trades_df[column].max()
            avg_value = trades_df[column].mean()
            min_value = trades_df[column].min()
            return max_value, avg_value, min_value
        return 0.0, 0.0, 0.0
    
    @staticmethod
    def calculate_sum(trades_df: pl.DataFrame, column: str) -> float:
        return trades_df[column].sum()
    
    @staticmethod
    def calculate_average_value(net_value: float, nr_trades: int) -> float:
        return net_value / nr_trades if nr_trades else 0.0

    @staticmethod
    def calculate_expected_value(winning_perc: float, avg_winning_value: float, losing_perc: float, avg_losing_value: float) -> float:
        return (winning_perc / 100 * avg_winning_value) - (losing_perc / 100 * avg_losing_value)

    @staticmethod
    def calculate_return_and_volatility_perc(trades_df: pl.DataFrame) -> (float, float, float):
        expected_log_return = trades_df[DatabaseAPI.TRADE_NETLOGRETURN].mean()
        total_log_return = trades_df[DatabaseAPI.TRADE_NETLOGRETURN].sum()
        log_return_volatility = trades_df[DatabaseAPI.TRADE_NETLOGRETURN].std()
        expected_return_perc = (math.exp(expected_log_return) - 1) * 100 if expected_log_return else 0.0
        total_return_perc = (math.exp(total_log_return) - 1) * 100 if total_log_return else 0.0
        return_volatility_perc = math.sqrt(math.exp(log_return_volatility**2) - 1) * 100 if log_return_volatility else 0.0
        return expected_return_perc, total_return_perc, return_volatility_perc

    @staticmethod
    def calculate_return_annualized_perc(start_timestamp: datetime, stop_timestamp: datetime, return_value_perc: float, trading_days: int = 365) -> float:
        if not return_value_perc:
            return 0.0
        days = (stop_timestamp - start_timestamp).days
        return (((1 + (return_value_perc / 100)) ** (trading_days / days)) - 1) * 100

    @staticmethod
    def calculate_volatility_annualized_perc(start_timestamp: datetime, stop_timestamp: datetime, volatility_value_perc: float, trading_days: int = 365) -> float:
        if not volatility_value_perc:
            return 0.0
        days = (stop_timestamp - start_timestamp).days
        return (volatility_value_perc / 100) * math.sqrt(trading_days / days) * 100
    
    @staticmethod
    def calculate_risk_to_reward(avg_winning_trade: float, avg_losing_trade: float)  -> float:
        return abs(avg_losing_trade) / avg_winning_trade if avg_winning_trade else 0.0
    
    @staticmethod
    def calculate_profit_factor(winning_pnl_value: float, losing_pnl_value: float) -> float:
        return winning_pnl_value / abs(losing_pnl_value) if losing_pnl_value else 0.0

    @staticmethod
    def calculate_max_and_mean_drawdown(initial_account: Account, trades_df: pl.DataFrame) -> (float, float, float, float):
        if trades_df.is_empty():
            return 0.0, 0.0, 0.0, 0.0
        initial_balance = initial_account.Balance
        cumulative_balance = trades_df[DatabaseAPI.TRADE_NETPNL].cum_sum() + pl.Series([initial_balance])
        running_max = cumulative_balance.cum_max()
        drawdown = running_max - cumulative_balance
        max_drawdown_value = drawdown.max()
        cumulative_max = running_max.max()
        max_drawdown_perc = (max_drawdown_value / cumulative_max) * 100 if cumulative_max else 0.0
        mean_drawdown_value = drawdown.mean()
        mean_drawdown_perc = (mean_drawdown_value / cumulative_max) * 100 if cumulative_max else 0.0
        return max_drawdown_value, max_drawdown_perc, mean_drawdown_value, mean_drawdown_perc

    @staticmethod
    def calculate_holding_times(trades_df: pl.DataFrame) -> (float, float, float):
        if trades_df.is_empty():
            return 0.0, 0.0, 0.0
        holding_times: pl.Series = trades_df[DatabaseAPI.TRADE_EXITTIMESTAMP] - trades_df[DatabaseAPI.TRADE_ENTRYTIMESTAMP]
        def format_timedelta(td: timedelta):
            days = td.days
            hours = td.seconds // 3600
            return days + hours / 100
        max_holding_time = format_timedelta(holding_times.max())
        avg_holding_time = format_timedelta(holding_times.mean())
        min_holding_time = format_timedelta(holding_times.min())
        return max_holding_time, avg_holding_time, min_holding_time

    @staticmethod
    def calculate_sharpe_ratio(annualized_return_perc: float, annualized_volatility_perc: float, risk_free_rate: float = 0.0) -> float:
        annualized_volatility_perc = annualized_volatility_perc if annualized_volatility_perc else StatisticsAPI.EPSILON
        return (annualized_return_perc - risk_free_rate) / annualized_volatility_perc

    @staticmethod
    def calculate_sortino_ratio(annualized_return_perc: float, downside_volatility_perc: float, risk_free_rate: float = 0.0) -> float:
        downside_volatility_perc = downside_volatility_perc if downside_volatility_perc else StatisticsAPI.EPSILON
        return (annualized_return_perc - risk_free_rate) / downside_volatility_perc if downside_volatility_perc else 0.0

    @staticmethod
    def calculate_calmar_ratio(annualized_return_perc: float, max_drawdown_perc: float, risk_free_rate: float = 0.0) -> float:
        max_drawdown_perc = max_drawdown_perc if max_drawdown_perc else StatisticsAPI.EPSILON
        return (annualized_return_perc - risk_free_rate) / abs(max_drawdown_perc) if max_drawdown_perc else 0.0

    @staticmethod
    def calculate_fitness_ratio(annualized_return_perc: float, mean_drawdown_perc: float, risk_free_rate: float = 0.0) -> float:
        mean_drawdown_perc = mean_drawdown_perc if mean_drawdown_perc else StatisticsAPI.EPSILON
        return (annualized_return_perc - risk_free_rate) / abs(mean_drawdown_perc) if mean_drawdown_perc else 0.0

    def calculate_independent_metrics(self, initial_account: Account, start_timestamp: datetime, stop_timestamp: datetime, total_trades_df: pl.DataFrame) -> dict:
        winning_trades_df, losing_trades_df = self.split_winning_losing_trades(total_trades_df)
        total_nr_trades = self.calculate_total_trades(total_trades_df)
        winning_nr_trades = self.calculate_total_trades(winning_trades_df)
        losing_nr_trades = self.calculate_total_trades(losing_trades_df)
        winning_rate_perc = self.calculate_rate_perc(winning_nr_trades, total_nr_trades)
        losing_rate_perc = self.calculate_rate_perc(losing_nr_trades, total_nr_trades)
        winning_max_trade, winning_avg_trade, winning_min_trade = self.calculate_min_avg_max(winning_nr_trades, winning_trades_df, DatabaseAPI.TRADE_NETPNL)
        losing_min_trade, losing_avg_trade, losing_max_trade = self.calculate_min_avg_max(losing_nr_trades, losing_trades_df, DatabaseAPI.TRADE_NETPNL)
        winning_max_pips, winning_avg_pips, winning_min_pips = self.calculate_min_avg_max(winning_nr_trades, winning_trades_df, DatabaseAPI.TRADE_NETPIPS)
        losing_min_pips, losing_avg_pips, losing_max_pips = self.calculate_min_avg_max(losing_nr_trades, losing_trades_df, DatabaseAPI.TRADE_NETPIPS)
        net_pips_value = self.calculate_sum(total_trades_df, DatabaseAPI.TRADE_NETPIPS)
        gross_pnl_value = self.calculate_sum(total_trades_df, DatabaseAPI.TRADE_GROSSPNL)
        commissions_value = self.calculate_sum(total_trades_df, DatabaseAPI.TRADE_COMMISSIONPNL)
        swaps_value = self.calculate_sum(total_trades_df, DatabaseAPI.TRADE_SWAPPNL)
        winning_pnl_value = self.calculate_sum(winning_trades_df, DatabaseAPI.TRADE_NETPNL)
        losing_pnl_value = self.calculate_sum(losing_trades_df, DatabaseAPI.TRADE_NETPNL)
        total_pnl_value = self.calculate_sum(total_trades_df, DatabaseAPI.TRADE_NETPNL)
        
        expected_winning_return_perc, winning_return_perc, winning_volatility_perc = self.calculate_return_and_volatility_perc(winning_trades_df)
        expected_losing_return_perc, losing_return_perc, losing_volatility_perc = self.calculate_return_and_volatility_perc(losing_trades_df)
        expected_net_return_perc, net_return_perc, net_volatility_perc = self.calculate_return_and_volatility_perc(total_trades_df)
        
        winning_return_annualized_perc = self.calculate_return_annualized_perc(start_timestamp, stop_timestamp, winning_return_perc)
        winning_volatility_annualized_perc = self.calculate_volatility_annualized_perc(start_timestamp, stop_timestamp, winning_volatility_perc)
        losing_return_annualized_perc = self.calculate_return_annualized_perc(start_timestamp, stop_timestamp, losing_return_perc)
        losing_volatility_annualized_perc = self.calculate_volatility_annualized_perc(start_timestamp, stop_timestamp, losing_volatility_perc)
        net_return_annualized_perc = self.calculate_return_annualized_perc(start_timestamp, stop_timestamp, net_return_perc)
        net_volatility_annualized_perc = self.calculate_volatility_annualized_perc(start_timestamp, stop_timestamp, net_volatility_perc)
        
        average_trade = self.calculate_average_value(total_pnl_value, total_nr_trades)
        average_pips = self.calculate_average_value(net_pips_value, total_nr_trades)
        expected_trade = self.calculate_expected_value(winning_rate_perc, winning_avg_trade, losing_rate_perc, losing_avg_trade)
        expected_pips = self.calculate_expected_value(winning_rate_perc, winning_avg_pips, losing_rate_perc, losing_avg_pips)
        
        risk_to_reward = self.calculate_risk_to_reward(winning_avg_trade, losing_avg_trade)
        profit_factor = self.calculate_profit_factor(winning_pnl_value, losing_pnl_value)
        max_drawdown_value, max_drawdown_perc, mean_drawdown_value, mean_drawdown_perc = self.calculate_max_and_mean_drawdown(initial_account, total_trades_df)
        max_holding_time, avg_holding_time, min_holding_time = self.calculate_holding_times(total_trades_df)
        
        sharpe_ratio = self.calculate_sharpe_ratio(net_return_annualized_perc, net_volatility_annualized_perc)
        sortino_ratio = self.calculate_sortino_ratio(net_return_annualized_perc, losing_volatility_annualized_perc)
        calmar_ratio = self.calculate_calmar_ratio(net_return_annualized_perc, max_drawdown_perc)
        fitness_ratio = self.calculate_fitness_ratio(net_return_annualized_perc, mean_drawdown_perc)
        
        return {self.NUMBEROFTRADES: total_nr_trades,
                
                self.NUMBEROFWINNINGTRADES: winning_nr_trades,
                self.WINNINGRATEPERC: winning_rate_perc,
                self.MAXWINNINGTRADE: winning_max_trade,
                self.AVERAGEWINNINGTRADE: winning_avg_trade,
                self.MINWINNINGTRADE: winning_min_trade,
                self.MAXWINNINGPIPS: winning_max_pips,
                self.AVERAGEWINNINGPIPS: winning_avg_pips,
                self.MINWINNINGPIPS: winning_min_pips,
                self.EXPECTEDWINNINGRETURNPERC: expected_winning_return_perc,
                self.WINNINGRETURNPERC: winning_return_perc,
                self.WINNINGRETURNANNPERC: winning_return_annualized_perc,
                self.WINNINGVOLATILITYPERC: winning_volatility_perc,
                self.WINNINGVOLATILITYANNPERC: winning_volatility_annualized_perc,
                
                self.NUMBEROFLOSINGTRADES: losing_nr_trades,
                self.LOSINGRATEPERC: losing_rate_perc,
                self.MAXLOSINGTRADE: losing_max_trade,
                self.AVERAGELOSINGTRADE: losing_avg_trade,
                self.MINLOSINGTRADE: losing_min_trade,
                self.MAXLOSINGPIPS: losing_max_pips,
                self.AVERAGELOSINGPIPS: losing_avg_pips,
                self.MINLOSINGPIPS: losing_min_pips,
                self.EXPECTEDLOSINGRETURNPERC: expected_losing_return_perc,
                self.LOSINGRETURNPERC: losing_return_perc,
                self.LOSINGRETURNANNPERC: losing_return_annualized_perc,
                self.LOSINGVOLATILITYPERC: losing_volatility_perc,
                self.LOSINGVOLATILITYANNPERC: losing_volatility_annualized_perc,
                
                self.AVERAGETRADE: average_trade,
                self.AVERAGEPIPS: average_pips,
                self.EXPECTEDTRADE: expected_trade,
                self.EXPECTEDPIPS: expected_pips,
                
                self.GROSSPNLVALUE:gross_pnl_value,
                self.COMMISSIONSPNLVALUE: commissions_value,
                self.SWAPSPNLVALUE: swaps_value,
                self.NETPNLVALUE: total_pnl_value,
                self.EXPECTEDNETRETURNPERC: expected_net_return_perc,
                self.NETRETURNPERC: net_return_perc,
                self.NETRETURNANNPERC: net_return_annualized_perc,
                self.NETVOLATILITYPERC: net_volatility_perc,
                self.NETVOLATILITYANNPERC: net_volatility_annualized_perc,
                self.NETPIPSVALUE: net_pips_value,
                
                self.PROFITFACTOR: profit_factor,
                self.RISKTOREWARDRATIO: risk_to_reward,
                self.MAXDRAWDOWNVALUE: max_drawdown_value,
                self.MAXDRAWDOWNPERC: max_drawdown_perc,
                self.MEANDRAWDOWNVALUE: mean_drawdown_value,
                self.MEANDRAWDOWNPERC: mean_drawdown_perc,
                self.MAXHOLDINGTIME: max_holding_time,
                self.AVERAGEHOLDINGTIME: avg_holding_time,
                self.MINHOLDINGTIME: min_holding_time,
                self.SHARPERATIO: sharpe_ratio,
                self.SORTINORATIO: sortino_ratio,
                self.CALMARRATIO: calmar_ratio,
                self.FITNESSRATIO: fitness_ratio}
        
    def calculate_dependent_metrics(self, initial_account: Account, start_timestamp: datetime, stop_timestamp: datetime, total_trades_df: pl.DataFrame, buy_metrics_label: str, sell_metrics_label: str, total_metrics_label: str) -> pl.DataFrame:
        buy_trades_df, sell_trades_df = self.split_buy_sell_trades(total_trades_df)
        buy_metrics_dict = self.calculate_independent_metrics(initial_account, start_timestamp, stop_timestamp, buy_trades_df)
        sell_metrics_dict = self.calculate_independent_metrics(initial_account, start_timestamp, stop_timestamp, sell_trades_df)
        total_metrics_dict = self.calculate_independent_metrics(initial_account, start_timestamp, stop_timestamp, total_trades_df)
        
        current_wining_streak = current_losing_streak = 0
        total_winning_streak = total_losing_streak = 0
        max_winning_streak_index = max_losing_streak_index = 0

        for idx, trade in enumerate(total_trades_df.iter_rows(named=True)):
            if trade[DatabaseAPI.TRADE_NETPNL] > 0:
                current_wining_streak += 1
                current_losing_streak = 0
            else:
                current_losing_streak += 1
                current_wining_streak = 0
        
            if current_wining_streak > total_winning_streak:
                max_winning_streak_index = idx
                total_winning_streak = current_wining_streak
            if current_losing_streak > total_losing_streak:
                max_losing_streak_index = idx
                total_losing_streak = current_losing_streak

        winning_streak_df = total_trades_df.slice(offset=max_winning_streak_index - total_winning_streak + 1, length=total_winning_streak)
        buy_winning_streak_df, sell_winning_streak_df = self.split_buy_sell_trades(winning_streak_df)
        buy_metrics_dict[self.MAXWINNINGSTREAK] = self.calculate_total_trades(buy_winning_streak_df)
        sell_metrics_dict[self.MAXWINNINGSTREAK] = self.calculate_total_trades(sell_winning_streak_df)
        total_metrics_dict[self.MAXWINNINGSTREAK] = self.calculate_total_trades(winning_streak_df)
        
        losing_streak_df = total_trades_df.slice(offset=max_losing_streak_index - total_losing_streak + 1, length=total_losing_streak)
        buy_losing_streak_df, sell_losing_streak_df = self.split_buy_sell_trades(losing_streak_df)
        buy_metrics_dict[self.MAXLOSINGSTREAK] = self.calculate_total_trades(buy_losing_streak_df)
        sell_metrics_dict[self.MAXLOSINGSTREAK] = self.calculate_total_trades(sell_losing_streak_df)
        total_metrics_dict[self.MAXLOSINGSTREAK] = self.calculate_total_trades(losing_streak_df)
        
        buy_metrics_list = [buy_metrics_dict[key] for key in self.Metrics]
        sell_metrics_list = [sell_metrics_dict[key] for key in self.Metrics]
        total_metrics_list = [total_metrics_dict[key] for key in self.Metrics]

        return pl.DataFrame(data={buy_metrics_label: buy_metrics_list,
                                  sell_metrics_label: sell_metrics_list,
                                  total_metrics_label: total_metrics_list},
                            strict=False)
    
    def data(self, initial_account: Account, start_timestamp: datetime, stop_timestamp: datetime) -> (pl.DataFrame, pl.DataFrame, pl.DataFrame):
        statistical_metrics_df = pl.DataFrame(data=self.Metrics, schema={self.STATISTICS_METRICS_LABEL: pl.String()})
        individual_df = self.sort_trades(self._data)
        individual_metrics_df = self.calculate_dependent_metrics(initial_account, start_timestamp, stop_timestamp, individual_df, self.BUY_METRICS_INDIVIDUAL, self.SELL_METRICS_INDIVIDUAL, self.TOTAL_METRICS_INDIVIDUAL)
        aggregated_df = self.sort_trades(self.aggregate_trades(self._data))
        aggregated_metrics_df = self.calculate_dependent_metrics(initial_account, start_timestamp, stop_timestamp, aggregated_df, self.BUY_METRICS_AGGREGATED, self.SELL_METRICS_AGGREGATED, self.TOTAL_METRICS_AGGREGATED)
        return individual_df, aggregated_df, pl.concat([statistical_metrics_df, individual_metrics_df, aggregated_metrics_df], how="horizontal")
