import clr
clr.AddReference("cAlgo.API")
from cAlgo.API import *

from Library.Parameters import ParametersAPI
from Library.Strategy.Rule.NNFX import NNFXStrategyAPI
from Library.System.Trading import TradingSystemAPI

class TradingBot:

    def on_start(self):
        parameterise = ParametersAPI()
        broker = self.Account.BrokerName.replace(" ", "")
        symbol = self.Symbol.Name.replace(" ", "")
        timeframe = self.TimeFrame.Name.replace(" ", "")
        group = "Forex"
        parameters = parameterise[broker][group][symbol][timeframe].Realtime["NNFX"]
        self.system = TradingSystemAPI(
            api=self,
            broker=broker,
            group=group,
            symbol=symbol,
            timeframe=timeframe,
            strategy=NNFXStrategyAPI,
            parameters=parameters
        )
        self.system.__enter__()
        self.system.start()

    def on_tick(self):
        self.system.on_tick()

    def on_bar_closed(self):
        self.system.on_bar_closed()

    def on_stop(self):
        self.system.on_shutdown()
        self.system.__exit__(None, None, None)

    def on_error(self, error):
        self.print(f"Error: {error}")

    def on_exception(self, exception):
        self.print(f"Exception: {exception}")
