from Library.Robots.Engine.Machine import MachineAPI
from Library.Robots.Strategy.Strategy import StrategyAPI
from Library.Robots.Parameters.Parameters import Parameters

class DownloadAPI(StrategyAPI):

    def __init__(self, money_management: Parameters, risk_management: Parameters, signal_management: Parameters):
        super().__init__(money_management, risk_management, signal_management)

    def risk_management(self) -> MachineAPI | None:
        return None

    def signal_management(self) -> MachineAPI | None:
        return None