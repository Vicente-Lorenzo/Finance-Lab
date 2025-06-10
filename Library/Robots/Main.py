import polars as pl
from typing import Type
from argparse import ArgumentParser

from Library.Logging.Logging import LoggingAPI
from Library.Logging.Console import ConsoleAPI
from Library.Logging.Telegram import TelegramAPI
from Library.Classes.Enums import VerboseType, SystemType, StrategyType
from Library.Parameters.Parameters import ParametersAPI, Parameters
from Library.Utils.Performance import time

from Library.Robots.Manager.Statistics import StatisticsAPI
from Library.Robots.Strategy.Strategy import StrategyAPI
from Library.Robots.Strategy.Human.Download import DownloadAPI
from Library.Robots.Strategy.Human.NNFX import NNFXAPI
from Library.Robots.Strategy.AI.DDPG import DDPGAPI
from Library.Robots.System.System import SystemAPI
from Library.Robots.System.Realtime import RealtimeAPI
from Library.Robots.System.Backtesting import BacktestingAPI
from Library.Robots.System.Optimisation import OptimisationAPI

pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_width_chars(-1)
pl.Config.set_fmt_str_lengths(1000)
pl.Config.set_fmt_table_cell_list_len(-1)

@time
def main():
    
    parameters: ParametersAPI = ParametersAPI()

    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--console", type=str, required=True, choices=[_.name for _ in VerboseType])
    parser.add_argument("--telegram", type=str, required=True, choices=[_.name for _ in VerboseType])
    parser.add_argument("--system", type=str, required=True, choices=[_.name for _ in SystemType])
    parser.add_argument("--strategy", type=str, required=True, choices=[_.name for _ in StrategyType])
    parser.add_argument("--broker", type=str, required=True, choices=parameters.Watchlist.Brokers)
    parser.add_argument("--group", type=str, required=True, choices=parameters.Watchlist.Symbols.keys())
    parser.add_argument("--symbol", type=str, required=True, choices=[symbol for group in parameters.Watchlist.Symbols.values() for symbol in group])
    parser.add_argument("--timeframe", type=str, required=True, choices=parameters.Watchlist.Timeframes)
    parser.add_argument("--iid", type=str, required=False)
    parser.add_argument("--start", type=str, required=False)
    parser.add_argument("--stop", type=str, required=False)
    parser.add_argument("--training", type=int, required=False)
    parser.add_argument("--validation", type=int, required=False)
    parser.add_argument("--testing", type=int, required=False)
    parser.add_argument("--balance", type=float, required=False)
    parser.add_argument("--spread", type=float, required=False)
    parser.add_argument("--fitness", type=str, required=False, choices=StatisticsAPI.Metrics)
    args = parser.parse_args()
    
    LoggingAPI.init(args.system, args.strategy, args.broker, args.group, args.symbol, args.timeframe)
    ConsoleAPI.level(console_verbose := VerboseType(VerboseType[args.console]))
    TelegramAPI.level(telegram_verbose := VerboseType(VerboseType[args.telegram]))
    
    console: ConsoleAPI = ConsoleAPI(class_name="Main", role_name="Execution Management")
    telegram: TelegramAPI = TelegramAPI(class_name="Main", role_name="Execution Management")
    
    console.info(lambda: "Initiated")
    telegram.info(lambda: "Initiated")
    
    strategy: Type[StrategyAPI] | None = None
    match args.strategy:
        case StrategyType.Download.name:
            strategy = DownloadAPI
        case StrategyType.NNFX.name:
            strategy = NNFXAPI
        case StrategyType.DDPG.name:
            strategy = DDPGAPI

    parameters: Parameters = parameters[args.broker][args.group][args.symbol][args.timeframe]

    system: SystemAPI | None = None
    match args.system:
        case SystemType.Realtime.name:
            if args.iid is None:
                parser.error("--iid is required for Realtime System")
            params: Parameters = parameters.Realtime[args.strategy]
            system = RealtimeAPI(broker=args.broker,
                                 group=args.group,
                                 symbol=args.symbol,
                                 timeframe=args.timeframe,
                                 strategy=strategy,
                                 parameters=params,
                                 iid=args.iid)
        case SystemType.Backtesting.name:
            if args.start is None:
                parser.error("--start is required for Backtesting System")
            if args.stop is None:
                parser.error("--stop is required for Backtesting System")
            if args.balance is None:
                parser.error("--balance is required for Backtesting System")
            if args.spread is None:
                parser.error("--spread is required for Backtesting System")
            params: Parameters = parameters.Backtesting[args.strategy]
            system = BacktestingAPI(broker=args.broker,
                                    group=args.group,
                                    symbol=args.symbol,
                                    timeframe=args.timeframe,
                                    strategy=strategy,
                                    parameters=params,
                                    start=args.start,
                                    stop=args.stop,
                                    balance=args.balance,
                                    spread=args.spread)
        case SystemType.Optimisation.name:
            if args.start is None:
                parser.error("--start is required for Optimisation System")
            if args.stop is None:
                parser.error("--stop is required for Optimisation System")
            if args.training is None:
                parser.error("--training is required for Optimisation System")
            if args.validation is None:
                parser.error("--validation is required for Optimisation System")
            if args.testing is None:
                parser.error("--testing is required for Optimisation System")
            if args.balance is None:
                parser.error("--balance is required for Optimisation System")
            if args.spread is None:
                parser.error("--spread is required for Optimisation System")
            if args.fitness is None:
                parser.error("--fitness is required for Optimisation System")
            params: Parameters = parameters.Backtesting[args.strategy]
            config: Parameters = parameters.Optimisation[args.strategy]
            system = OptimisationAPI(broker=args.broker,
                                     group=args.group,
                                     symbol=args.symbol,
                                     timeframe=args.timeframe,
                                     strategy=strategy,
                                     parameters=params,
                                     configuration=config,
                                     start=args.start,
                                     stop=args.stop,
                                     training=args.training,
                                     validation=args.validation,
                                     testing=args.testing,
                                     balance=args.balance,
                                     spread=args.spread,
                                     fitness=args.fitness,
                                     console=console_verbose,
                                     telegram=telegram_verbose)

    console.info(lambda: "Executing")
    telegram.info(lambda: "Executing")

    with system:
        system.start()
        system.join()

    console.info(lambda: "Terminated")
    telegram.info(lambda: "Terminated")

if __name__ == "__main__":
    main()
