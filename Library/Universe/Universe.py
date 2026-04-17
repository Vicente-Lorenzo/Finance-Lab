from __future__ import annotations

from dataclasses import dataclass

from Library.Database.Datapoint import DatapointAPI

@dataclass(slots=True, kw_only=True)
class UniverseAPI(DatapointAPI):
    pass