from __future__ import annotations

from dash import html, dcc
from typing import TYPE_CHECKING
from typing_extensions import Self
if TYPE_CHECKING: from Library.App import AppAPI

from Library.App.Component import Component
from Library.Logging import HandlerLoggingAPI

class PageAPI:

    MEMORY_STORAGE_ID: dict = None
    SESSION_STORAGE_ID: dict = None
    LOCAL_STORAGE_ID: dict = None

    def __init__(self, *,
                 app: AppAPI,
                 path: str,
                 anchor: str = None,
                 endpoint: str = None,
                 button: str = None,
                 description: str = None,
                 indexed: bool = True,
                 content: Component = None,
                 sidebar: Component = None,
                 navigation: Component = None) -> None:

        self._log_: HandlerLoggingAPI = HandlerLoggingAPI(PageAPI.__name__)

        self.app: AppAPI = app
        self.path: str = path
        self.button: str = button
        self.description: str = description
        self.indexed: bool = indexed

        self._anchor_: str = anchor
        self._endpoint_: str = endpoint

        self._sidebar_: Component | list[Component] = sidebar
        self._content_: Component | list[Component] = content
        self._navigation_: Component = navigation

        self._parent_: PageAPI | None = None
        self._children_: list[PageAPI] = []

        self._initialized_: bool = False

    def identify(self, *, page: str = None, type: str, name: str) -> dict:
        if not page: page = self.endpoint
        return self.app.identify(page=page, type=type, name=name)

    def register(self, *, page: str = None, type: str, name: str) -> dict:
        if not page: page = self.endpoint
        return self.app.register(page=page, type=type, name=name)

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
    def parent(self) -> Self:
        return self._parent_
    @property
    def children(self) -> list[Self]:
        return self._children_
    @property
    def family(self) -> list[Self]:
        return [self] + self.children

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

    def _init_ids_(self) -> None:
        self.MEMORY_STORAGE_ID: dict = self.register(type="storage", name="memory")
        self.SESSION_STORAGE_ID: dict = self.register(type="storage", name="session")
        self.LOCAL_STORAGE_ID: dict = self.register(type="storage", name="local")
        self.ids()

    def _init_hidden_(self) -> Component:
        return html.Div([
            dcc.Store(id=self.MEMORY_STORAGE_ID, storage_type="memory", data={}),
            dcc.Store(id=self.SESSION_STORAGE_ID, storage_type="session", data={}),
            dcc.Store(id=self.LOCAL_STORAGE_ID, storage_type="local", data={}),
        ])

    def _init_layout_(self) -> None:
        sidebar = self._sidebar_ or self.sidebar()
        self._log_.debug(lambda: f"Loaded Sidebar Layout")
        content = self._content_ or self.content()
        self._log_.debug(lambda: f"Loaded Content Layout")
        hidden = self._init_hidden_()
        self._log_.debug(lambda: f"Loaded Hidden Layout")
        self._content_ = [content, hidden] if isinstance(content, Component) else [*content, hidden]
        self._sidebar_ = [sidebar] if isinstance(sidebar, Component) else sidebar

    def _init_(self) -> None:
        if self._initialized_: return
        self._init_ids_()
        self._log_.info(lambda: f"Initialized IDs: {self}")
        self._init_layout_()
        self._log_.info(lambda: f"Initialized Layout: {self}")
        self._initialized_ = True

    def ids(self) -> None:
        pass

    def sidebar(self) -> Component | list[Component]:
        return self.app.NOT_INDEXED_LAYOUT

    def content(self) -> Component | list[Component]:
        return self.app.NOT_INDEXED_LAYOUT

    def __repr__(self):
        return f"{self.description} @ {self.endpoint}"
