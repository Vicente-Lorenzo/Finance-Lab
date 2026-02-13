from __future__ import annotations

from dash import dcc
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

        self._app_: AppAPI = app
        self.path: str = path
        self.button: str = button
        self.description: str = description

        self._add_backward_parent_: bool = add_backward_parent
        self._add_backward_children_: bool = add_backward_children
        self._add_current_parent_: bool = add_current_parent
        self._add_current_children_: bool = add_current_children
        self._add_forward_parent_: bool = add_forward_parent
        self._add_forward_children_: bool = add_forward_children

        self._anchor_: str = anchor
        self._endpoint_: str = endpoint

        self._sidebar_: list[Component] = self.normalize(sidebar)
        self._content_: list[Component] = self.normalize(content)
        self._navigation_: list[Component] = self.normalize(navigation)

        self._parent_: PageAPI | None = None
        self._children_: list[PageAPI] = []

        self._initialized_: bool = False

    @staticmethod
    def normalize(element: Component | list[Component]) -> list[Component]:
        if element is None: return []
        return [element] if isinstance(element, Component) else list(element)

    def identify(self, *, page: str = None, type: str, name: str, portable: str = "", **kwargs) -> dict:
        page = page or self.endpoint or "global"
        return self._app_.identify(page=page, type=type, name=name, portable=portable, **kwargs)

    def register(self, *, page: str = None, type: str, name: str, portable: str = "", **kwargs) -> dict:
        page = page or self.endpoint or "global"
        return self._app_.register(page=page, type=type, name=name, portable=portable, **kwargs)

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

    def _init_ids_(self) -> None:
        self.MEMORY_STORAGE_ID: dict = self.register(type="storage", name="memory")
        self.SESSION_STORAGE_ID: dict = self.register(type="storage", name="session")
        self.LOCAL_STORAGE_ID: dict = self.register(type="storage", name="local")
        self.ids()

    def _init_hidden_(self) -> list[Component]:
        memory = dcc.Store(id=self.MEMORY_STORAGE_ID, storage_type="memory", data={})
        session = dcc.Store(id=self.SESSION_STORAGE_ID, storage_type="session", data={})
        local = dcc.Store(id=self.LOCAL_STORAGE_ID, storage_type="local", data={})
        return self.normalize([memory, session, local])

    def _init_layout_(self) -> None:
        hidden = self._init_hidden_()
        self._log_.debug(lambda: f"Loaded Hidden Layout")
        content = self.normalize(self._content_ or self.content())
        self._content_ = self.normalize([*content, *hidden])
        self._log_.debug(lambda: f"Loaded Content Layout")
        sidebar = self.normalize(self._sidebar_ or self.sidebar())
        self._sidebar_ = self.normalize([*sidebar])
        self._log_.debug(lambda: f"Loaded Sidebar Layout")
        navigation = self.normalize(self._navigation_ or self.navigation())
        self._navigation_ = self.normalize([*navigation])
        self._log_.debug(lambda: f"Loaded Navigation Layout")

    def _init_(self) -> None:
        if self._initialized_: return
        self._init_ids_()
        self._log_.info(lambda: f"Initialized IDs: {self}")
        self._init_layout_()
        self._log_.info(lambda: f"Initialized Layout: {self}")
        self._initialized_ = True

    def ids(self) -> None:
        pass

    def content(self) -> Component | list[Component]:
        return self.normalize(self._app_.NOT_INDEXED_LAYOUT)

    def sidebar(self) -> Component | list[Component]:
        return self.normalize(self._app_.NOT_INDEXED_LAYOUT)

    def navigation(self) -> Component | list[Component]:
        return self.normalize([])

    def __repr__(self):
        return f"{self.description} @ {self.endpoint}"
