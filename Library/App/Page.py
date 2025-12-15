from typing import Self

from Library.Logging import HandlerLoggingAPI
from Library.Utility import Component

class PageAPI:

    def __init__(self,
                 app,
                 path: str,
                 button: str = None,
                 description: str = None,
                 indexed: bool = True,
                 layout: Component = None):

        self._log_: HandlerLoggingAPI = HandlerLoggingAPI(self.__class__.__name__)

        self.app = app
        self.path: str = path
        self.button: str = button
        self.description: str = description
        self.indexed: bool = indexed

        self._anchor_: str | None = None
        self._endpoint_: str | None = None

        self._parent_: PageAPI | None = None
        self._children_: list[PageAPI] = []

        self._layout_: Component = layout or self.build()
        self._navigation_: Component | None = None

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
    @property
    def children(self) -> list[Self]:
        return self._children_
    @property
    def family(self) -> list[Self]:
        return [self] + self.children

    @property
    def layout(self):
        return self._layout_
    @property
    def navigation(self):
        return self._navigation_
    @navigation.setter
    def navigation(self, navigation: Component) -> None:
        self._navigation_ = navigation

    def attach(self, parent: Self):
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
        self._log_.debug(lambda: f"Attached Page = {self.endpoint} to Parent = {parent.endpoint}")

    def merge(self, page: Self):
        self._parent_ = page._parent_
        self._children_ = page._children_
        if self._parent_ and page in self._parent_._children_:
            idx = self._parent_._children_.index(page)
            self._parent_._children_[idx] = self
        for child in self._children_:
            child._parent_ = self
        self._log_.debug(lambda: f"Merged Pages = {page.endpoint}")

    def __repr__(self):
        return f"{self.description} @ {self.endpoint}"
