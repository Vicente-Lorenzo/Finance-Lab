from __future__ import annotations

import dash
import inspect
from enum import Enum
from functools import wraps
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable
from typing_extensions import Self

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
        elif hasattribute(context, self.component):
            component = getattribute(context, self.component)
            load: str = "Page Attribute" if isinstance(context, PageAPI) else "Global Attribute"
        elif isinstance(context, PageAPI) and hasattribute(context.app, self.component):
            component = getattribute(context.app, self.component)
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

class Injection(Enum):
    Disabled = 0
    Hidden = 1
    Prepend = 2
    Append = 3
    @classmethod
    def coerce(cls, value) -> Self:
        if isinstance(value, cls):
            return value
        if value is False:
            return cls.Disabled
        if value is True:
            return cls.Hidden
        return cls.Disabled

def flatten(*args) -> list:
    flat = []
    for arg in args:
        if isinstance(arg, (tuple, list)):
            flat.extend(arg)
        else:
            flat.append(arg)
    return flat

def sort(*args):
    outputs, inputs, states, others = [], [], [], []
    for arg in flatten(*args):
        if isinstance(arg, (Output, dash.dependencies.Output)): outputs.append(arg)
        elif isinstance(arg, (Input, dash.dependencies.Input)): inputs.append(arg)
        elif isinstance(arg, (State, dash.dependencies.State)): states.append(arg)
        else: others.append(arg)
    return outputs, inputs, states, others

def organize(original_args: list, inject_args: list, mode: Injection):
    o_out, o_in, o_st, o_oth = sort(original_args)
    i_out, i_in, i_st, i_oth = sort(inject_args)
    if mode == Injection.Prepend:
        all_out, all_in, all_st, all_oth = i_out + o_out, i_in + o_in, i_st + o_st, i_oth + o_oth
    else:
        all_out, all_in, all_st, all_oth = o_out + i_out, o_in + i_in, o_st + i_st, o_oth + i_oth
    return all_out, all_in, all_st, all_oth, o_out, o_in, o_st, i_out, i_in, i_st

def callback(
        *callback_args,
        callback_js: bool,
        on_app_click: bool | Injection,
        on_app_loading: bool | Injection,
        on_app_reloading: bool | Injection,
        on_app_unloading: bool | Injection,
        on_app_memory_clean: bool | Injection,
        on_app_session_clean: bool | Injection,
        on_app_local_clean: bool | Injection,
        on_app_clean_reset: bool | Injection,
        **callback_kwargs):
    def decorator(func):
        func._callback_ = True
        func._callback_js_ = callback_js
        func._callback_kwargs_ = callback_kwargs
        func._on_app_click_ = on_app_click
        func._on_app_loading_ = on_app_loading
        func._on_app_reloading_ = on_app_reloading
        func._on_app_unloading_ = on_app_unloading
        func._on_app_memory_clean_ = on_app_memory_clean
        func._on_app_session_clean_ = on_app_session_clean
        func._on_app_local_clean_ = on_app_local_clean
        func._on_app_clean_reset_ = on_app_clean_reset
        func._callback_args_ = flatten(*sort(callback_args))
        return func
    return decorator

def clientside_callback(
        *callback_args,
        on_app_init: bool | Injection = Injection.Disabled,
        on_app_click: bool | Injection = Injection.Disabled,
        on_app_loading: bool | Injection = Injection.Disabled,
        on_app_reloading: bool | Injection = Injection.Disabled,
        on_app_unloading: bool | Injection = Injection.Disabled,
        on_app_memory_clean: bool | Injection = Injection.Disabled,
        on_app_session_clean: bool | Injection = Injection.Disabled,
        on_app_local_clean: bool | Injection = Injection.Disabled,
        on_app_clean_reset: bool | Injection = Injection.Disabled,
        **callback_kwargs):
    return callback(
        *callback_args,
        callback_js=True,
        on_app_click=on_app_click,
        on_app_loading=on_app_loading,
        on_app_reloading=on_app_reloading,
        on_app_unloading=on_app_unloading,
        on_app_memory_clean=on_app_memory_clean,
        on_app_session_clean=on_app_session_clean,
        on_app_local_clean=on_app_local_clean,
        on_app_clean_reset=on_app_clean_reset,
        prevent_initial_call=Injection.coerce(on_app_init) is Injection.Disabled,
        **callback_kwargs
    )

def serverside_callback(
        *callback_args,
        on_app_init: bool | Injection = Injection.Disabled,
        on_app_click: bool | Injection = Injection.Disabled,
        on_app_loading: bool | Injection = Injection.Disabled,
        on_app_reloading: bool | Injection = Injection.Disabled,
        on_app_unloading: bool | Injection = Injection.Disabled,
        on_app_memory_clean: bool | Injection = Injection.Disabled,
        on_app_session_clean: bool | Injection = Injection.Disabled,
        on_app_local_clean: bool | Injection = Injection.Disabled,
        on_app_clean_reset: bool | Injection = Injection.Disabled,
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
        on_app_click=on_app_click,
        on_app_loading=on_app_loading,
        on_app_reloading=on_app_reloading,
        on_app_unloading=on_app_unloading,
        on_app_memory_clean=on_app_memory_clean,
        on_app_session_clean=on_app_session_clean,
        on_app_local_clean=on_app_local_clean,
        on_app_clean_reset=on_app_clean_reset,
        prevent_initial_call=Injection.coerce(on_app_init) is Injection.Disabled,
        background=background,
        manager=manager,
        running=running,
        progress=progress,
        cancel=cancel,
        memoize=memoize,
        **callback_kwargs
    )

def _inject_callback_(original_args, inject_args, inject_func, mode):
    all_out, all_in, all_st, all_oth, o_out, o_in, o_st, i_out, i_in, i_st = organize(original_args, inject_args, mode)
    all_args = [*all_out, *all_in, *all_st, *all_oth]
    prepend = mode == Injection.Prepend
    inject_func = inject_func if mode == Injection.Hidden else None
    return all_args, prepend, inject_func, len(o_out), len(o_in), len(o_st), len(i_out), len(i_in), len(i_st), len(all_out), len(all_in), len(all_st)

def inject_serverside_callback(
        inject_func: Callable | None,
        inject_args: tuple | list,
        original_func: Callable,
        original_args: tuple | list,
        mode: Injection):
    all_args, prepend, inject_func, n_o_out, n_o_in, n_o_st, n_i_out, n_i_in, n_i_st, n_all_out, n_all_in, n_all_st = _inject_callback_(original_args, inject_args, inject_func, mode)
    wants_kwargs = False
    accepted_params = set()
    if inject_func:
        sig = inspect.signature(inject_func)
        wants_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        accepted_params = set(sig.parameters.keys())
    @wraps(original_func)
    def wrapped(*args, **kwargs):
        input_vals = args[:n_all_in]
        state_vals = args[n_all_in:]
        if prepend:
            inject_inputs, original_inputs = input_vals[:n_i_in], input_vals[n_i_in:]
            inject_states, original_states = state_vals[:n_i_st], state_vals[n_i_st:]
        else:
            original_inputs, inject_inputs = input_vals[:n_o_in], input_vals[n_o_in:]
            original_states, inject_states = state_vals[:n_o_st], state_vals[n_o_st:]
        original_result = original_func(*original_inputs, *original_states, **kwargs)
        inject_result = None
        if inject_func:
            available_kwargs = {
                "inject_inputs": inject_inputs,
                "inject_states": inject_states,
                "original_inputs": original_inputs,
                "original_states": original_states
            }
            if wants_kwargs:
                kwargs_to_pass = available_kwargs
            else:
                kwargs_to_pass = {k: v for k, v in available_kwargs.items() if k in accepted_params}
            inject_result = inject_func(original_result, **kwargs_to_pass)
        o_res_list = [original_result] if n_o_out == 1 else list(original_result) if n_o_out > 1 else []
        if n_o_out > 1 and not isinstance(original_result, (list, tuple)):
            raise ValueError(f"Expected {n_o_out} outputs from original function.")
        i_res_list = []
        if n_i_out > 0:
            if inject_result is None: i_res_list = [dash.no_update] * n_i_out
            elif n_i_out == 1: i_res_list = [inject_result]
            else:
                if not isinstance(inject_result, (list, tuple)): raise ValueError(f"Expected {n_i_out} outputs from inject function.")
                i_res_list = list(inject_result)
        final_list = i_res_list + o_res_list if prepend else o_res_list + i_res_list
        if n_all_out == 0: return None
        if n_all_out == 1: return final_list[0]
        return tuple(final_list)
    return wrapped, all_args

def inject_clientside_callback(
        inject_func: str | None,
        inject_args: tuple | list,
        original_js: str,
        original_args: tuple | list,
        mode: Injection):
    all_args, prepend, inject_func, n_o_out, n_o_in, n_o_st, n_i_out, n_i_in, n_i_st, n_all_out, n_all_in, n_all_st = _inject_callback_(original_args, inject_args, inject_func, mode)
    handler_src = "null" if inject_func is None else f"({inject_func})"
    no_update = "window.dash_clientside.no_update"
    wrapped_js = f"""
    function() {{
        const originalFn = ({original_js});
        const injectFn = {handler_src};
        const args = Array.prototype.slice.call(arguments);
        const inputVals = args.slice(0, {n_all_in});
        const stateVals = args.slice({n_all_in});
        let originalInputs, injectInputs, originalStates, injectStates;
        if ({str(prepend).lower()}) {{
            injectInputs = inputVals.slice(0, {n_i_in});
            originalInputs = inputVals.slice({n_i_in});
            injectStates = stateVals.slice(0, {n_i_st});
            originalStates = stateVals.slice({n_i_st});
        }} else {{
            originalInputs = inputVals.slice(0, {n_o_in});
            injectInputs = inputVals.slice({n_o_in});
            originalStates = stateVals.slice(0, {n_o_st});
            injectStates = stateVals.slice({n_o_st});
        }}
        const originalResult = originalFn.apply(null, originalInputs.concat(originalStates));
        let injectResult = null;
        if (injectFn) {{
            injectResult = injectFn(originalResult, injectInputs, injectStates, originalInputs, originalStates);
        }}
        let oResList = [];
        if ({n_o_out} === 1) oResList = [originalResult];
        else if ({n_o_out} > 1) {{
            if (!Array.isArray(originalResult)) throw new Error("Expected {n_o_out} outputs from original callback.");
            oResList = originalResult;
        }}
        let iResList = [];
        if ({n_i_out} > 0) {{
            if (injectResult === null || injectResult === undefined) iResList = Array({n_i_out}).fill({no_update});
            else if ({n_i_out} === 1) iResList = [injectResult];
            else {{
                if (!Array.isArray(injectResult)) throw new Error("Expected {n_i_out} outputs from injected callback.");
                iResList = injectResult;
            }}
        }}
        const finalList = {str(prepend).lower()} ? iResList.concat(oResList) : oResList.concat(iResList);
        if ({n_all_out} <= 1) return finalList.length > 0 ? finalList[0] : undefined;
        return finalList;
    }}
    """
    return wrapped_js, all_args
