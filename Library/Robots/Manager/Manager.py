from math import floor

from Library.Parameters import Parameters

from Library.Robots.Manager import AccountAPI, SymbolAPI, PositionAPI, StatisticsAPI

class ManagerAPI:

    def __init__(self, manager_management: Parameters):
        self.ManagerManagement = manager_management
        self.Account: AccountAPI = AccountAPI()
        self.Symbol: SymbolAPI = SymbolAPI()
        self.Positions: PositionAPI = PositionAPI()
        self.Statistics: StatisticsAPI = StatisticsAPI()

    def normalize_volume(self, volume: float, apply=floor) -> float:
        normalized = apply(volume / self.Symbol.VolumeInUnitsStep) * self.Symbol.VolumeInUnitsStep
        return max(self.Symbol.VolumeInUnitsMin, min(normalized, self.Symbol.VolumeInUnitsMax))

    def volume_by_amount(self, amount: float, sl_pips: float) -> float:
        return amount / (sl_pips * self.Symbol.PipValue) * self.Symbol.LotSize

    def volume_by_risk(self, risk_percentage: float, sl_pips: float):
        amount = self.Account.Balance * risk_percentage / 100
        volume = self.volume_by_amount(amount, sl_pips)
        return self.normalize_volume(volume)

    def data(self):
        return self.Positions.data()

    def __repr__(self):
        return repr(self.data())