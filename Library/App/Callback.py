from __future__ import annotations

import dash
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING: from Library.App import AppAPI
from Library.App import PageAPI
from Library.Utility.Typing import hasattribute, getattribute

def callback(callback_js: bool, *callback_args, **callback_kwargs):
    def decorator(func):
        func._callback_ = True
        func._callback_js_ = callback_js
        func._callback_args_ = callback_args
        func._callback_kwargs_ = callback_kwargs
        return func
    return decorator

def clientside_callback(*callback_args, **callback_kwargs):
    return callback(True, *callback_args, **callback_kwargs)

def serverside_callback(*callback_args, **callback_kwargs):
    return callback(False, *callback_args, **callback_kwargs)

class Trigger(ABC):
    def __init__(self, component: str | dict, property: str):
        self.component: str | dict = component
        self.property: str = property
    @abstractmethod
    def build(self, context: AppAPI | PageAPI) -> tuple[dict, str]:
        trigger: str = self.__class__.__name__
        if isinstance(self.component, dict):
            component = context.identify(**self.component)
            load: str = "Hardcode Dict"
        elif isinstance(self.component, str) and hasattribute(context, self.component):
            component = getattribute(context, self.component)
            load: str = "Page Attribute" if isinstance(context, PageAPI) else "Global Attribute"
        elif isinstance(self.component, str) and isinstance(context, PageAPI) and hasattribute(context._app_, self.component):
            component = getattribute(context._app_, self.component)
            load: str = "Global Attribute"
        else:
            component = self.component
            load: str = "Hardcode String"
        context._log_.debug(lambda: f"Loaded {load} ({trigger}): {component} @ {self.property}")
        return component, self.property

class Output(Trigger):
    def __init__(self, component: str | dict, property: str, allow_duplicate: bool = True):
        super().__init__(component=component, property=property)
        self.allow_duplicate: bool = allow_duplicate
    def build(self, context: AppAPI | PageAPI) -> dash.Output:
        component, property = super().build(context=context)
        return dash.Output(component_id=component, component_property=property, allow_duplicate=self.allow_duplicate)

class Input(Trigger):
    def __init__(self, component: str | dict, property: str, allow_optional: bool = True):
        super().__init__(component=component, property=property)
        self.allow_optional: bool = allow_optional
    def build(self, context: AppAPI | PageAPI) -> dash.Input:
        component, property = super().build(context=context)
        return dash.Input(component_id=component, component_property=property, allow_optional=self.allow_optional)

class State(Trigger):
    def __init__(self, component: str | dict, property: str, allow_optional: bool = True):
        super().__init__(component=component, property=property)
        self.allow_optional: bool = allow_optional
    def build(self, context: AppAPI | PageAPI) -> dash.State:
        component, property = super().build(context=context)
        return dash.State(component_id=component, component_property=property, allow_optional=self.allow_optional)
