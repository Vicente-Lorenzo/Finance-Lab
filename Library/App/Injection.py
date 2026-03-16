import threading
from abc import ABC, abstractmethod
from typing import Callable, Tuple, Any
from dash.exceptions import PreventUpdate

from Library.App.Session import TriggerAPI
from Library.App.Callback import Input, Output, State, InjectionType

class InjectionAPI(ABC):
    def __init__(self, flag: str):
        self.flag = flag
        self.mapping: dict[str, int] = {}
        self.counter: int = 0
        self.index: int = 0
        self.lock: threading.RLock = threading.RLock()
    @abstractmethod
    def args(self, is_page: bool) -> list:
        pass
    @abstractmethod
    def py(self, payload: dict) -> Any:
        pass
    @abstractmethod
    def js(self, app) -> str:
        pass
    def __call__(self, app, is_page: bool) -> Tuple[Callable | None, str | None]:
        return self.py, self.js(app)
    def register(self, page: str = None) -> None:
        with self.lock:
            self.counter += 1
            key = page or "global"
            self.mapping[key] = self.mapping.get(key, 0) + 1
    def increment(self) -> None:
        with self.lock:
            self.index += 1
    def reset(self) -> None:
        with self.lock:
            self.index = 0
    def count(self, app: bool = True, page: bool | str = False) -> int:
        with self.lock:
            total = 0
            if app:
                total += self.mapping.get("global", 0)
            if isinstance(page, str):
                total += self.mapping.get(page, 0)
            elif page:
                total += sum(v for k, v in self.mapping.items() if k != "global")
            return total

class ClickInjectionAPI(InjectionAPI):
    def __init__(self):
        super().__init__(flag="on_click")
    def args(self, is_page: bool) -> list:
        return []
    def py(self, payload: dict) -> Any:
        original_inputs = payload.get("original_inputs", [])
        clicks = original_inputs[0] if original_inputs else None
        if not clicks: raise PreventUpdate
        return payload.get("original_outputs")
    def js(self, app) -> str:
        return app.asset(path="Callbacks/Click.js")

class CleanInjectionAPI(InjectionAPI, ABC):
    def py(self, payload: dict) -> Any:
        injected_inputs = payload.get("injected_inputs", [])
        clicks = injected_inputs[0] if len(injected_inputs) > 0 else None
        trigger = injected_inputs[1] if len(injected_inputs) > 1 else None
        if not clicks and not trigger: raise PreventUpdate
        return payload.get("original_outputs")
    def js(self, app) -> str:
        return app.asset(path="Callbacks/Clean.js")

class CleanMemoryInjectionAPI(CleanInjectionAPI):
    def __init__(self):
        super().__init__(flag="on_clean_memory")
    def args(self, is_page: bool) -> list:
        from Library.App import AppAPI
        return [
            Input(AppAPI.GLOBAL_CLEAN_MEMORY_BUTTON_ID, "n_clicks"),
            Input(AppAPI.GLOBAL_CLEAN_MEMORY_ASYNC_ID, "data")
        ]

class CleanSessionInjectionAPI(CleanInjectionAPI):
    def __init__(self):
        super().__init__(flag="on_clean_session")
    def args(self, is_page: bool) -> list:
        from Library.App import AppAPI
        return [
            Input(AppAPI.GLOBAL_CLEAN_SESSION_BUTTON_ID, "n_clicks"),
            Input(AppAPI.GLOBAL_CLEAN_SESSION_ASYNC_ID, "data")
        ]

class CleanLocalInjectionAPI(CleanInjectionAPI):
    def __init__(self):
        super().__init__(flag="on_clean_local")
    def args(self, is_page: bool) -> list:
        from Library.App import AppAPI
        return [
            Input(AppAPI.GLOBAL_CLEAN_LOCAL_BUTTON_ID, "n_clicks"),
            Input(AppAPI.GLOBAL_CLEAN_LOCAL_ASYNC_ID, "data")
        ]

class CleanResetInjectionAPI(CleanInjectionAPI):
    def __init__(self):
        super().__init__(flag="on_clean_reset")
    def args(self, is_page: bool) -> list:
        from Library.App import AppAPI
        return [
            Input(AppAPI.GLOBAL_CLEAN_RESET_BUTTON_ID, "n_clicks"),
            Input(AppAPI.GLOBAL_CLEAN_RESET_ASYNC_ID, "data")
        ]

class LoadingInjectionAPI(InjectionAPI):
    def __init__(self, flag: str = "on_loading"):
        super().__init__(flag=flag)
    def args(self, is_page: bool) -> list:
        from Library.App import AppAPI, PageAPI
        if is_page:
            return [
                Output(PageAPI.PAGE_LOADING_ASYNC_ID, "data"),
                Input(AppAPI.GLOBAL_LOADING_ASYNC_ID, "data"),
                State(PageAPI.PAGE_LOADING_ASYNC_ID, "data")
            ]
        return [
            Input(AppAPI.GLOBAL_LOADING_ASYNC_ID, "data")
        ]
    def py(self, payload: dict) -> Any:
        injected_inputs = payload.get("injected_inputs", [])
        trigger = injected_inputs[0] if injected_inputs else None
        if not trigger: raise PreventUpdate
        return TriggerAPI(**trigger).trigger().dict()
    def js(self, app) -> str:
        return app.asset(path="Callbacks/Trigger.js")
    def __call__(self, app, is_page: bool) -> Tuple[Callable | None, str | None]:
        return (self.py, self.js(app)) if is_page else (None, None)

class ReloadingInjectionAPI(LoadingInjectionAPI):
    def __init__(self):
        super().__init__(flag="on_reloading")
    def args(self, is_page: bool) -> list:
        from Library.App import AppAPI, PageAPI
        if is_page:
            return [
                Output(PageAPI.PAGE_RELOADING_ASYNC_ID, "data"),
                Input(AppAPI.GLOBAL_RELOADING_ASYNC_ID, "data"),
                State(PageAPI.PAGE_RELOADING_ASYNC_ID, "data")
            ]
        return [
            Input(AppAPI.GLOBAL_RELOADING_ASYNC_ID, "data")
        ]

class UnloadingInjectionAPI(LoadingInjectionAPI):
    def __init__(self):
        super().__init__(flag="on_unloading")
    def args(self, is_page: bool) -> list:
        from Library.App import AppAPI, PageAPI
        if is_page:
            return [
                Output(PageAPI.PAGE_UNLOADING_ASYNC_ID, "data"),
                Input(AppAPI.GLOBAL_UNLOADING_ASYNC_ID, "data"),
                State(PageAPI.PAGE_UNLOADING_ASYNC_ID, "data")
            ]
        return [
            Input(AppAPI.GLOBAL_UNLOADING_ASYNC_ID, "data")
        ]

class InjectorAPI:
    def __init__(self, app):
        self.app = app
        self.on_click = ClickInjectionAPI()
        self.on_clean_memory = CleanMemoryInjectionAPI()
        self.on_clean_session = CleanSessionInjectionAPI()
        self.on_clean_local = CleanLocalInjectionAPI()
        self.on_clean_reset = CleanResetInjectionAPI()
        self.on_loading = LoadingInjectionAPI()
        self.on_reloading = ReloadingInjectionAPI()
        self.on_unloading = UnloadingInjectionAPI()
        
        self.injections = [
            self.on_click,
            self.on_clean_memory,
            self.on_clean_session,
            self.on_clean_local,
            self.on_clean_reset,
            self.on_loading,
            self.on_reloading,
            self.on_unloading
        ]

    def match(self, func) -> list[InjectionAPI]:
        matched = []
        for inj in self.injections:
            mode = InjectionType.coerce(getattr(func, inj.flag, False))
            if mode is not InjectionType.Disabled:
                matched.append(inj)
        return matched