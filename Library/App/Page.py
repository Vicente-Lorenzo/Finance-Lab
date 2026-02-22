from __future__ import annotations

from dash import dcc
from typing import TYPE_CHECKING
from typing_extensions import Self

if TYPE_CHECKING: from Library.App import AppAPI
from Library.App.Callback import *
from Library.App.Session import TriggerAPI
from Library.App.Component import Component
from Library.Logging import HandlerLoggingAPI

class PageAPI:

    PAGE_LOADING_TRIGGER_ID: dict
    PAGE_RELOADING_TRIGGER_ID: dict
    PAGE_UNLOADING_TRIGGER_ID: dict

    PAGE_MEMORY_STORAGE_ID: dict
    PAGE_SESSION_STORAGE_ID: dict
    PAGE_PERMANENT_STORAGE_ID: dict

    def __init__(self, *,
                 app: AppAPI,
                 path: str,
                 anchor: str = None,
                 endpoint: str = None,
                 redirect: str = None,
                 button: str = None,
                 description: str = None,
                 content: Component | list[Component] = None,
                 sidebar: Component | list[Component] = None,
                 navigation: Component | list[Component] = None,
                 add_backward_parent: bool = True,
                 add_backward_children: bool = False,
                 add_current_parent: bool = False,
                 add_current_children: bool = True,
                 add_forward_parent: bool = False,
                 add_forward_children: bool = True) -> None:

        self._log_ = HandlerLoggingAPI(PageAPI.__name__)

        self.app: AppAPI = app
        self.path: str = path
        self.button: str = button
        self.description: str = description

        self._add_backward_parent_: bool = add_backward_parent
        self._add_backward_children_: bool = add_backward_children
        self._add_current_parent_: bool = add_current_parent
        self._add_current_children_: bool = add_current_children
        self._add_forward_parent_: bool = add_forward_parent
        self._add_forward_children_: bool = add_forward_children

        self._anchor_: str = self.app.anchorize(anchor, relative=True) if anchor else anchor
        self._endpoint_: str = self.app.endpointize(endpoint, relative=True) if endpoint else endpoint
        self._redirect_: str = self.app.endpointize(redirect, relative=True) if redirect else redirect

        self._sidebar_: list[Component] = self.normalize(sidebar)
        self._content_: list[Component] = self.normalize(content)
        self._navigation_: list[Component] = self.normalize(navigation)

        self._parent_: PageAPI | None = None
        self._children_: list[PageAPI] = []

        self._loaders_: list[str] = []
        self._reloaders_: list[str] = []
        self._unloaders_: list[str] = []

        self._initialized_: bool = False

    @staticmethod
    def normalize(element: Component | list[Component]) -> list[Component]:
        if element is None: return []
        return [element] if isinstance(element, Component) else list(element)

    def identify(self, *, page: str = None, type: str, name: str, portable: str = "", **kwargs) -> dict:
        page = page or self.endpoint or "global"
        return self.app.identify(page=page, type=type, name=name, portable=portable, **kwargs)

    def register(self, *, page: str = None, type: str, name: str, portable: str = "", **kwargs) -> dict:
        page = page or self.endpoint or "global"
        return self.app.register(page=page, type=type, name=name, portable=portable, **kwargs)

    @property
    def anchor(self) -> str:
        return self._anchor_
    @anchor.setter
    def anchor(self, anchor: str) -> None:
        self._anchor_ = self._anchor_ or anchor
    @property
    def endpoint(self) -> str:
        return self._endpoint_
    @endpoint.setter
    def endpoint(self, endpoint: str) -> None:
        self._endpoint_ = self._endpoint_ or endpoint
    @property
    def redirect(self) -> str:
        return self._redirect_ or self.endpoint

    @property
    def parent(self) -> Self:
        return self._parent_
    @property
    def children(self) -> list[Self]:
        return self._children_
    @property
    def family(self) -> list[Self]:
        return [self] + self.children

    def backwards(self) -> list[Self]:
        if not self.parent: return []
        if self._add_backward_parent_: return self.parent.family if self._add_backward_children_ else [self.parent]
        else: return self.parent.children if self._add_backward_children_ else []
    def currents(self) -> list[Self]:
        if self._add_current_parent_: return self.family if self._add_current_children_ else [self]
        else: return self.children if self._add_current_children_ else []
    def forwards(self, current: Self) -> list[Self]:
        if self._add_forward_parent_: return current.family if self._add_forward_children_ else [current]
        else: return current.children if self._add_forward_children_ else []

    def attach(self, parent: Self) -> None:
        if parent is None:
            return
        if self._parent_ is parent:
            return
        if self._parent_:
            self._parent_._children_.remove(self)
        self._parent_ = parent
        if self in parent._children_:
            idx = parent._children_.index(self)
            parent._children_[idx] = self
        else:
            parent._children_.append(self)
        self._log_.info(lambda: f"Attached {parent} (Parent) to {self} (Child)")

    def merge(self, page: Self) -> None:
        parent = page._parent_
        self._parent_ = parent
        if parent:
            idx = parent._children_.index(page)
            parent._children_[idx] = self
        self._children_ = list(page._children_)
        for child in self._children_:
            child._parent_ = self
        page._parent_ = None
        page._children_.clear()
        self._log_.info(lambda: f"Merged {page} (Old) into {self} (New)")

    def loader(self, name: str) -> dict:
        self._loaders_.append(name)
        return self.PAGE_LOADING_TRIGGER_ID

    def reloader(self, name: str) -> dict:
        self._reloaders_.append(name)
        return self.PAGE_RELOADING_TRIGGER_ID

    def unloader(self, name: str) -> dict:
        self._unloaders_.append(name)
        return self.PAGE_UNLOADING_TRIGGER_ID

    def _init_ids_(self) -> None:
        self.PAGE_LOADING_TRIGGER_ID: dict = self.register(type="trigger", name="loading")
        self.PAGE_RELOADING_TRIGGER_ID: dict = self.register(type="trigger", name="reloading")
        self.PAGE_UNLOADING_TRIGGER_ID: dict = self.register(type="trigger", name="unloading")

        self.PAGE_MEMORY_STORAGE_ID: dict = self.register(type="storage", name="memory")
        self.PAGE_SESSION_STORAGE_ID: dict = self.register(type="storage", name="session")
        self.PAGE_PERMANENT_STORAGE_ID: dict = self.register(type="storage", name="permanent")

        self.ids()

    def _init_hidden_(self) -> list[Component]:
        loading = dcc.Store(id=self.PAGE_LOADING_TRIGGER_ID, storage_type="memory", data=dict())
        reloading = dcc.Store(id=self.PAGE_RELOADING_TRIGGER_ID, storage_type="memory", data=dict())
        unloading = dcc.Store(id=self.PAGE_UNLOADING_TRIGGER_ID, storage_type="memory", data=dict())
        memory = dcc.Store(id=self.PAGE_MEMORY_STORAGE_ID, storage_type="memory", data=dict())
        session = dcc.Store(id=self.PAGE_SESSION_STORAGE_ID, storage_type="session", data=dict())
        permanent = dcc.Store(id=self.PAGE_PERMANENT_STORAGE_ID, storage_type="local", data=dict())
        return self.normalize([loading, reloading, unloading, memory, session, permanent])

    def _init_content_(self) -> list[Component]:
        hidden = self._init_hidden_()
        self._log_.debug(lambda: f"Loaded Hidden Layout")
        content = self.normalize(self._content_ or self.content())
        return self.normalize([*content, *hidden])

    def _init_sidebar_(self) -> list[Component]:
        sidebar = self.normalize(self._sidebar_ or self.sidebar())
        return self.normalize([*sidebar])

    def _init_navigation_(self) -> list[Component]:
        navigation = self.normalize(self._navigation_ or self.navigation())
        return self.normalize([*navigation])

    def _init_layout_(self) -> None:
        self._content_ = self._init_content_()
        self._log_.debug(lambda: f"Loaded Content Layout")
        self._sidebar_ = self._init_sidebar_()
        self._log_.debug(lambda: f"Loaded Sidebar Layout")
        self._navigation_ = self._init_navigation_()
        self._log_.debug(lambda: f"Loaded Navigation Layout")

    def _init_(self) -> None:
        if self._initialized_: return
        self._init_ids_()
        self._log_.info(lambda: f"Initialized IDs: {self}")
        self._init_layout_()
        self._log_.info(lambda: f"Initialized Layout: {self}")
        self._initialized_ = True

    @serverside_callback(
        Output("PAGE_LOADING_TRIGGER_ID", "data"),
        Input("GLOBAL_LOADING_TRIGGER_ID", "data"),
        State("PAGE_LOADING_TRIGGER_ID", "data")
    )
    def _page_loading_location_callback_(self, _, loading: dict):
        loading = TriggerAPI(**(loading or {}))
        return loading.trigger().dict()

    @serverside_callback(
        Output("PAGE_RELOADING_TRIGGER_ID", "data"),
        Input("GLOBAL_RELOADING_TRIGGER_ID", "data"),
        State("PAGE_RELOADING_TRIGGER_ID", "data")
    )
    def _page_reloading_location_callback_(self, _, reloading: dict):
        reloading = TriggerAPI(**(reloading or {}))
        return reloading.trigger().dict()

    def ids(self) -> None:
        pass

    def content(self) -> Component | list[Component]:
        return self.normalize(self.app.GLOBAL_NOT_INDEXED_LAYOUT)

    def sidebar(self) -> Component | list[Component]:
        return self.normalize(self.app.GLOBAL_NOT_INDEXED_LAYOUT)

    def navigation(self) -> Component | list[Component]:
        return self.normalize([])

    def __repr__(self) -> str:
        return repr(f"{self.description} @ {self.endpoint}")
