from __future__ import annotations

from typing import ClassVar
from dataclasses import dataclass

from Library.Database.Datapoint import DatapointAPI

@dataclass(kw_only=True)
class MarketAPI(DatapointAPI):
    Database: ClassVar[str] = DatapointAPI.Database
    Schema: ClassVar[str] = "Market"
    Table: ClassVar[str] = "Market"