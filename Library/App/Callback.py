from __future__ import annotations

import dash
from functools import wraps
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

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

def organize(*callback_args):
    outputs, inputs, states, others = [], [], [], []
    for arg in callback_args:
        if isinstance(arg, (Output, dash.dependencies.Output)): outputs.append(arg)
        elif isinstance(arg, (Input, dash.dependencies.Input)): inputs.append(arg)
        elif isinstance(arg, (State, dash.dependencies.State)): states.append(arg)
        else: others.append(arg)
    return outputs, inputs, states, others

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
        func._callback_args_ = flatten(*organize(*flatten(*callback_args)))
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

def override_serverside_callback(
        handler_func: Callable | None,
        handler_args: tuple | list,
        original_func: Callable,
        original_args: tuple | list):
    def normalize_return(value, n_outputs: int) -> tuple:
        if n_outputs == 0:
            return tuple()
        if n_outputs == 1:
            return (value,)
        if not isinstance(value, (tuple, list)):
            raise TypeError(f"Expected {n_outputs} outputs, got {type(value).__name__}.")
        if len(value) != n_outputs:
            raise ValueError(f"Expected {n_outputs} outputs, got {len(value)}.")
        return tuple(value)
    h_out, h_in, h_st, h_other = organize(*flatten(*handler_args))
    o_out, o_in, o_st, o_other = organize(*flatten(*original_args))
    new_out = [*o_out, *h_out]
    new_in  = [*o_in,  *h_in]
    new_st  = [*o_st,  *h_st]
    new_other = [*o_other, *h_other]
    n_h_in, n_o_in = len(h_in), len(o_in)
    n_h_st, n_o_st = len(h_st), len(o_st)
    n_h_out, n_o_out = len(h_out), len(o_out)
    n_new_out = len(new_out)
    @wraps(original_func)
    def wrapped(*args, **kwargs):
        input_vals = tuple(args[: len(new_in)])
        state_vals = tuple(args[len(new_in): len(new_in) + len(new_st)])
        orig_inputs = input_vals[:n_o_in]
        hidden_inputs = input_vals[n_o_in:n_o_in + n_h_in]
        orig_states = state_vals[:n_o_st]
        hidden_states = state_vals[n_o_st:n_o_st + n_h_st]
        orig_result = original_func(*orig_inputs, *orig_states, **kwargs)
        if n_h_out == 0:
            if handler_func is None:
                return orig_result
            out = handler_func(orig_result, hidden_inputs=hidden_inputs, hidden_states=hidden_states)
            return orig_result if out is None else out
        base = normalize_return(orig_result, n_o_out)
        if handler_func is None:
            pad = (dash.no_update,) * n_h_out
            return *base, *pad
        extra = handler_func(orig_result, hidden_inputs=hidden_inputs, hidden_states=hidden_states)
        if extra is None:
            pad = (dash.no_update,) * n_h_out
            return *base, *pad
        if n_new_out == 1 and not isinstance(extra, (tuple, list)):
            return extra
        if isinstance(extra, (tuple, list)):
            extra_t = tuple(extra)
            if len(extra_t) == n_h_out:
                return *base, *extra_t
            if len(extra_t) == n_new_out:
                return extra_t
        raise ValueError(f"handler_func returned an unexpected shape. Expected None, {n_h_out} (extras), or {n_new_out} (full).")
    new_args = [*new_out, *new_in, *new_st, *new_other]
    return wrapped, new_args

def override_clientside_callback(
        handler_func: str | None,
        handler_args: tuple | list,
        original_js: str,
        original_args: tuple | list):
    h_out, h_in, h_st, h_other = organize(*flatten(*handler_args))
    o_out, o_in, o_st, o_other = organize(*flatten(*original_args))
    new_out = [*o_out, *h_out]
    new_in  = [*o_in,  *h_in]
    new_st  = [*o_st,  *h_st]
    new_other = [*o_other, *h_other]
    n_h_in, n_o_in = len(h_in), len(o_in)
    n_h_st, n_o_st = len(h_st), len(o_st)
    n_h_out, n_o_out = len(h_out), len(o_out)
    n_new_out = len(new_out)
    n_new_inputs = len(new_in)
    n_new_states = len(new_st)
    no_update = "window.dash_clientside.no_update"
    handler_src = "null" if handler_func is None else f"({handler_func})"
    wrapped_js = f"""
    function() {{
        const userFn = ({original_js});
        const handlerFn = {handler_src};
        const args = Array.prototype.slice.call(arguments);
        const inputVals = args.slice(0, {n_new_inputs});
        const stateVals = args.slice({n_new_inputs}, {n_new_inputs} + {n_new_states});
        const origInputs = inputVals.slice(0, {n_o_in});
        const hiddenInputs = inputVals.slice({n_o_in}, {n_o_in} + {n_h_in});
        const origStates = stateVals.slice(0, {n_o_st});
        const hiddenStates = stateVals.slice({n_o_st}, {n_o_st} + {n_h_st});
        const baseResult = userFn.apply(null, origInputs.concat(origStates));
        if ({n_h_out} === 0) {{
            if (!handlerFn) {{
                return baseResult;
            }}
            const out = handlerFn(baseResult, hiddenInputs, hiddenStates);
            return (out === undefined || out === null) ? baseResult : out;
        }}
        function normalizeBase(value) {{
            if ({n_o_out} === 0) return [];
            if ({n_o_out} === 1) return [value];
            if (!Array.isArray(value) || value.length !== {n_o_out}) {{
                throw new Error("Expected {n_o_out} outputs from user callback.");
            }}
            return value;
        }}
        const baseArr = normalizeBase(baseResult);
        if (!handlerFn) {{
            const pad = Array({n_h_out}).fill({no_update});
            return baseArr.concat(pad);
        }}
        const extra = handlerFn(baseResult, hiddenInputs, hiddenStates);
        if (extra === undefined || extra === null) {{
            const pad = Array({n_h_out}).fill({no_update});
            return baseArr.concat(pad);
        }}
        if ({n_new_out} === 1 && !Array.isArray(extra)) {{
            return extra;
        }}
        if (Array.isArray(extra)) {{
            if (extra.length === {n_h_out}) {{
                return baseArr.concat(extra);
            }}
            if (extra.length === {n_new_out}) {{
                return extra;
            }}
        }}
        throw new Error("handler_func returned unexpected shape. Expected null, {n_h_out} (extras), or {n_new_out} (full).");
    }}
    """
    new_args = [*new_out, *new_in, *new_st, *new_other]
    return wrapped_js, new_args
