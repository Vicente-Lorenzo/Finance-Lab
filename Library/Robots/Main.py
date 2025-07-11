import polars as pl
from typing import Type
from pathlib import Path
from argparse import ArgumentParser

from Library.Logging import *
from Library.Classes import VerboseType, SystemType, StrategyType
from Library.Parameters import ParametersAPI, Parameters
from Library.Utils import time

from Library.Robots.Manager import StatisticsAPI
from Library.Robots.Strategy import *
from Library.Robots.System import *

@time
def main():

    pl.Config.set_tbl_cols(-1)
    pl.Config.set_tbl_rows(-1)
    pl.Config.set_tbl_width_chars(-1)
    pl.Config.set_fmt_str_lengths(1000)
    pl.Config.set_fmt_table_cell_list_len(-1)

    execution = Path(__file__).parent.name

    parameterise: ParametersAPI = ParametersAPI()

    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--console", type=str, required=True, choices=[_.name for _ in VerboseType])
    parser.add_argument("--telegram", type=str, required=True, choices=[_.name for _ in VerboseType])
    parser.add_argument("--file", type=str, required=True, choices=[_.name for _ in VerboseType])

    parser.add_argument("--system", type=str, required=True, choices=[_.name for _ in SystemType])
    parser.add_argument("--strategy", type=str, required=True, choices=[_.name for _ in StrategyType])
    parser.add_argument("--broker", type=str, required=True, choices=parameterise.Watchlist.Brokers)
    parser.add_argument("--group", type=str, required=True, choices=parameterise.Watchlist.Symbols.keys())
    parser.add_argument("--symbol", type=str, required=True, choices=[symbol for group in parameterise.Watchlist.Symbols.values() for symbol in group])
    parser.add_argument("--timeframe", type=str, required=True, choices=parameterise.Watchlist.Timeframes)

    parser.add_argument("--iid", type=str, required=False)

    parser.add_argument("--start", type=str, required=False)
    parser.add_argument("--stop", type=str, required=False)
    parser.add_argument("--balance", type=float, required=False)
    parser.add_argument("--spread", type=float, required=False)

    parser.add_argument("--training", type=int, required=False)
    parser.add_argument("--validation", type=int, required=False)
    parser.add_argument("--testing", type=int, required=False)
    parser.add_argument("--episodes", type=int, required=False)
    parser.add_argument("--fitness", type=str, required=False, choices=StatisticsAPI.Metrics)

    args = parser.parse_args()

    LoggingAPI.init(
        System=args.system,
        Strategy=args.strategy,
        Broker=args.broker,
        Group=args.group,
        Symbol=args.symbol,
        Timeframe=args.timeframe
    )

    ConsoleAPI.setup(VerboseType(VerboseType[args.console]))
    TelegramAPI.setup(VerboseType(VerboseType[args.telegram]), args.group)
    FileAPI.setup(VerboseType(VerboseType[args.file]), execution)

    log = HandlerAPI(Class=execution, Subclass="Execution Management")

    @time
    @log.trace
    def launch():

        strategy: Type[StrategyAPI] | None = None
        match args.strategy:
            case StrategyType.Download.name:
                strategy = DownloadStrategyAPI
            case StrategyType.NNFX.name:
                strategy = NNFXStrategyAPI
            case StrategyType.DDPG.name:
                strategy = DDPGStrategyAPI

        parameters: Parameters = parameterise[args.broker][args.group][args.symbol][args.timeframe]

        system: SystemAPI | None = None
        match args.system:
            case SystemType.Realtime.name:
                if args.iid is None:
                    parser.error("--iid is required for Realtime System")
                params: Parameters = parameters.Realtime[args.strategy]
                system = RealtimeSystemAPI(
                    broker=args.broker,
                    group=args.group,
                    symbol=args.symbol,
                    timeframe=args.timeframe,
                    strategy=strategy,
                    parameters=params,
                    iid=args.iid
                )
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
                system = BacktestingSystemAPI(
                    broker=args.broker,
                    group=args.group,
                    symbol=args.symbol,
                    timeframe=args.timeframe,
                    strategy=strategy,
                    parameters=params,
                    start=args.start,
                    stop=args.stop,
                    balance=args.balance,
                    spread=args.spread
                )
            case SystemType.Optimisation.name:
                if args.start is None:
                    parser.error("--start is required for Optimisation System")
                if args.stop is None:
                    parser.error("--stop is required for Optimisation System")
                if args.balance is None:
                    parser.error("--balance is required for Optimisation System")
                if args.spread is None:
                    parser.error("--spread is required for Optimisation System")
                if args.training is None:
                    parser.error("--training is required for Optimisation System")
                if args.validation is None:
                    parser.error("--validation is required for Optimisation System")
                if args.testing is None:
                    parser.error("--testing is required for Optimisation System")
                if args.fitness is None:
                    parser.error("--fitness is required for Optimisation System")
                params: Parameters = parameters.Backtesting[args.strategy]
                config: Parameters = parameters.Optimisation[args.strategy]
                system = OptimisationSystemAPI(
                    broker=args.broker,
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
                    fitness=args.fitness
                )
            case SystemType.Learning.name:
                if args.start is None:
                    parser.error("--start is required for Learning System")
                if args.stop is None:
                    parser.error("--stop is required for Learning System")
                if args.balance is None:
                    parser.error("--balance is required for Learning System")
                if args.spread is None:
                    parser.error("--spread is required for Learning System")
                if args.episodes is None:
                    parser.error("--episodes is required for Learning System")
                if args.fitness is None:
                    parser.error("--fitness is required for Learning System")
                params: Parameters = parameters.Learning[args.strategy]
                system = LearningSystemAPI(
                    broker=args.broker,
                    group=args.group,
                    symbol=args.symbol,
                    timeframe=args.timeframe,
                    strategy=strategy,
                    parameters=params,
                    start=args.start,
                    stop=args.stop,
                    balance=args.balance,
                    spread=args.spread,
                    episodes=args.episodes,
                    fitness=args.fitness
                )

        log.debug(lambda: "Executing")

        with system:
            system.start()
            system.join()

    launch()

if __name__ == "__main__":
    main()
