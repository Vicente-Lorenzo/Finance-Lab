import math
from datetime import datetime
from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI

@dataclass(slots=True, kw_only=True)
class CycleAPI(DataclassAPI):
    Value: float = field(init=True, repr=True)
    Period: int = field(default=None, init=True, repr=True)

    @property
    def Radian(self) -> float:
        return 2 * math.pi * self.Value / self.Period
    @property
    def Sin(self):
        return math.sin(self.Radian)
    @property
    def Cos(self):
        return math.cos(self.Radian)

@dataclass(slots=True, kw_only=True)
class TimestampAPI(DataclassAPI):
    Timestamp: datetime = field(init=True, repr=True)

    @property
    def Year(self) -> CycleAPI:
        return CycleAPI(Value=self.Timestamp.year)
    @property
    def Month(self) -> CycleAPI:
        return CycleAPI(Value=self.Timestamp.month, Period=12)
    @property
    def Weekday(self) -> CycleAPI:
        return CycleAPI(Value=self.Timestamp.weekday(), Period=7)
    @property
    def Day(self) -> CycleAPI:
        return CycleAPI(Value=self.Timestamp.day, Period=31)
    @property
    def Hour(self) -> CycleAPI:
        return CycleAPI(Value=self.Timestamp.hour, Period=24)
    @property
    def Minute(self) -> CycleAPI:
        return CycleAPI(Value=self.Timestamp.minute, Period=60)
    @property
    def Second(self) -> CycleAPI:
        return CycleAPI(Value=self.Timestamp.second, Period=60)
    @property
    def Millisecond(self) -> CycleAPI:
        return CycleAPI(Value=self.Timestamp.microsecond, Period=1000)
