from __future__ import annotations

import dash
from typing import TYPE_CHECKING
if TYPE_CHECKING: from Library.App import AppAPI
from abc import ABC, abstractmethod

def callback(*args, **kwargs):
    def decorator(func):
        func._callback_ = True
        func._callback_args_ = args
        func._callback_kwargs_ = kwargs
        return func
    return decorator

class Trigger(ABC):
    def __init__(self, component: str, property: str):
        self.component: str = component
        self.property: str = property
    @abstractmethod
    def build(self, app: AppAPI):
        component = getattr(app, self.component) if hasattr(app, self.component) else self.component
        return component, self.property

class Output(Trigger):
    def __init__(self, component: str, property: str, allow_duplicate: bool = True):
        super().__init__(component=component, property=property)
        self.allow_duplicate: bool = allow_duplicate
    def build(self, app: AppAPI):
        component, property = super().build(app=app)
        return dash.Output(component_id=component, component_property=property, allow_duplicate=self.allow_duplicate)

class Input(Trigger):
    def __init__(self, component: str, property: str, allow_optional: bool = True):
        super().__init__(component=component, property=property)
        self.allow_optional: bool = allow_optional
    def build(self, app: AppAPI):
        component, property = super().build(app=app)
        return dash.Input(component_id=component, component_property=property, allow_optional=self.allow_optional)

class State(Trigger):
    def __init__(self, component: str, property: str, allow_optional: bool = True):
        super().__init__(component=component, property=property)
        self.allow_optional: bool = allow_optional
    def build(self, app: AppAPI):
        component, property = super().build(app=app)
        return dash.State(component_id=component, component_property=property, allow_optional=self.allow_optional)
