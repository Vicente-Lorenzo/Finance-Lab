from Library.Parameters import Parameters

from Library.Robots.Engine import MachineAPI
from Library.Robots.Strategy import StrategyAPI
from Library.Models.DDPG import DDPGAgentAPI

class DDPGStrategyAPI(StrategyAPI):

    def __init__(self,
                 money_management: Parameters,
                 risk_management: Parameters,
                 signal_management: Parameters):

        super().__init__(money_management, risk_management, signal_management)

    def risk_management(self) -> MachineAPI | None:
        return None

    def signal_management(self) -> MachineAPI | None:
        return None
