from __future__ import annotations

import dash
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from Library.App.Component import Component
if TYPE_CHECKING: from Library.App import AppAPI, PageAPI
from Library.Utility.Typing import hasattribute, getattribute

class Trigger(ABC):
    def __init__(self, component: str | dict, property: str):
        self.component: str | dict = component
        self.property: str = property
    @abstractmethod
    def build(self, context: AppAPI | PageAPI) -> tuple[dict, str]:
        from Library.App.Page import PageAPI
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

def flatten(*callback_args) -> list:
    flat = []
    for arg in callback_args:
        if isinstance(arg, (tuple, list)):
            flat.extend(arg)
        else:
            flat.append(arg)
    return flat

def organize(*callback_args) -> tuple[list[dash.Output], list[dash.Input], list[dash.State], list]:
    outputs = []
    inputs = []
    states = []
    others = []
    for arg in callback_args:
        if isinstance(arg, Output): outputs.append(arg)
        elif isinstance(arg, Input): inputs.append(arg)
        elif isinstance(arg, State): states.append(arg)
        else: others.append(arg)
    return *outputs, *inputs, *states, *others

def callback(*callback_args,
             callback_js: bool,
             callback_loading: bool,
             callback_reloading: bool,
             callback_unloading: bool,
             **callback_kwargs):
    def decorator(func):
        func._callback_ = True
        func._callback_js_ = callback_js
        func._callback_kwargs_ = callback_kwargs
        func._callback_loading_ = callback_loading
        func._callback_reloading_ = callback_reloading
        func._callback_unloading_ = callback_unloading
        func._callback_args_ = organize(*flatten(*callback_args))
        if callback_loading:
            print(func._callback_args_)
        return func
    return decorator

def clientside_callback(
        *callback_args,
        enable_loading_call: bool = False,
        enable_reloading_call: bool = False,
        enable_unloading_call: bool = False,
        enable_initial_call: bool = False,
        **callback_kwargs):
    return callback(
        *callback_args,
        callback_js=True,
        callback_loading=enable_loading_call,
        callback_reloading=enable_reloading_call,
        callback_unloading=enable_unloading_call,
        prevent_initial_call=not enable_initial_call,
        **callback_kwargs
    )

def serverside_callback(
    *callback_args,
    enable_loading_call: bool = False,
    enable_reloading_call: bool = False,
    enable_unloading_call: bool = False,
    enable_initial_call: bool = False,
    background: bool = False,
    memoize: bool = False,
    manager: str = None,
    running: list[Component] = None,
    progress: list[Component] = None,
    cancel: list[Component] = None,
    **callback_kwargs):
    return callback(
        *callback_args,
        callback_js=False,
        callback_loading=enable_loading_call,
        callback_reloading=enable_reloading_call,
        callback_unloading=enable_unloading_call,
        prevent_initial_call=not enable_initial_call,
        background=background,
        manager=manager,
        running=running,
        progress=progress,
        cancel=cancel,
        memoize=memoize,
        **callback_kwargs
    )
