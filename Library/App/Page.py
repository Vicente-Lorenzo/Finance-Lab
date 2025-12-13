from typing import Self
from abc import ABC, abstractmethod

from Library.Logging import HandlerLoggingAPI
from Library.Utility import Component

class PageAPI(ABC):

    def __init__(self,
                 app,
                 path: str,
                 button: str = None,
                 description: str = None,
                 indexed: bool = True):

        self._log_: HandlerLoggingAPI = HandlerLoggingAPI(self.__class__.__name__)

        self.app = app
        self.path: str = path
        self.button: str = button
        self.description: str = description
        self.indexed: bool = indexed

        self._anchor_: str | None = None
        self._endpoint_: str | None = None

        self._parent_: Self = None
        self._children_: list[Self] = []

        self._layout_: Component = self.build()
        self._navigation_: Component | None = None

    @abstractmethod
    def build(self) -> Component:
        return self.app.DEVELOPMENT_LAYOUT

    @property
    def anchor(self) -> str:
        return self._anchor_
    @anchor.setter
    def anchor(self, anchor: str) -> None:
        self._anchor_ = anchor
    @property
    def endpoint(self) -> str:
        return self._endpoint_
    @endpoint.setter
    def endpoint(self, endpoint: str) -> None:
        self._endpoint_ = endpoint

    @property
    def parent(self) -> Self:
        return self._parent_
    @parent.setter
    def parent(self, parent: Self) -> None:
        if parent is None: return
        if parent.parent is not None:
            parent.children = self
        self._parent_ = parent
    @property
    def children(self) -> list[Self]:
        return self._children_
    @children.setter
    def children(self, children: Self) -> None:
        self._children_.append(children)
    @property
    def family(self) -> list[Self]:
        return [self] + self.children

    @property
    def layout(self):
        return self._layout_
    @property
    def navigation(self):
        return self._navigation_

    def __repr__(self):
        return f"{self.description} @ {self.endpoint}"
