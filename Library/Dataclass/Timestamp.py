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
    DateTime: datetime = field(init=True, repr=True)

    @property
    def Year(self) -> CycleAPI:
        return CycleAPI(Value=self.DateTime.year)
    @property
    def Month(self) -> CycleAPI:
        return CycleAPI(Value=self.DateTime.month, Period=12)
    @property
    def Weekday(self) -> CycleAPI:
        return CycleAPI(Value=self.DateTime.weekday(), Period=7)
    @property
    def Day(self) -> CycleAPI:
        return CycleAPI(Value=self.DateTime.day, Period=31)
    @property
    def Hour(self) -> CycleAPI:
        return CycleAPI(Value=self.DateTime.hour, Period=24)
    @property
    def Minute(self) -> CycleAPI:
        return CycleAPI(Value=self.DateTime.minute, Period=60)
    @property
    def Second(self) -> CycleAPI:
        return CycleAPI(Value=self.DateTime.second, Period=60)
    @property
    def Millisecond(self) -> CycleAPI:
        return CycleAPI(Value=self.DateTime.microsecond, Period=1000)
