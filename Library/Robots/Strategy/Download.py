from Agents.Engine.Machine import MachineAPI
from Agents.Strategy.Strategy import StrategyAPI
from Agents.Parameters.Parameters import Parameters

class DownloadAPI(StrategyAPI):

    def __init__(self, money_management: Parameters, risk_management: Parameters, signal_management: Parameters):
        super().__init__(money_management, risk_management, signal_management)

    def risk_management(self) -> MachineAPI | None:
        return None

    def signal_management(self) -> MachineAPI | None:
        return None