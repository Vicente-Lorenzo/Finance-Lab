from abc import ABC, abstractmethod
import dash_bootstrap_components as dbc

from Library.Utility import Component

class ComponentAPI(Component, ABC):

    @abstractmethod
    def build(self) -> Component:
        raise NotImplementedError

    def __repr__(self):
        return repr(self.build())

class ButtonAPI(ComponentAPI):

    def __init__(self,
                 key: dict = None,
                 label: str = None,
                 background: str = "white",
                 border: str = "black",
                 size: str = "md",
                 vertical: bool = False,
                 classname: str = "component-button"):
        super().__init__()
        self._key_: dict = key or {}
        self._label_: str = label
        self._background_: str = background
        self._border_: str = border
        self._size_: str = size
        self._vertical_: bool = vertical
        self._classname_: str = classname

    def button(self) -> Component:
        return dbc.Button(
            children=self._label_,
            id=self._key_,
            color=self._background_,
            className=f"button"
        )

    def group(self) -> list[Component]:
        return [self.button()]

    def build(self) -> Component:
        return dbc.ButtonGroup(
            children=self.group(),
            size=self._size_,
            vertical=self._vertical_,
            style={"border": f"1px solid {self._border_}", "border-radius": "6px"},
            className=f"{self._classname_}-group"
        )

class PageButtonAPI(ButtonAPI):

    def __init__(self,
                 key: dict = None,
                 label: str = None,
                 target: str = None,
                 background: str = "white",
                 size: str = "md",
                 vertical: bool = False,
                 classname: str = "component-page-button"):
        super().__init__(
            key=key,
            label=label,
            background=background,
            size=size,
            vertical=vertical,
            classname=classname
        )
        self._target_: str = target

    def button(self) -> Component:
        return dbc.Button(
            children=self._label_,
            id=self._key_,
            href=self._target_,
            title="Open Page",
            color=self._background_,
            className=f"button"
        )

    def external(self) -> Component:
        return dbc.Button(
            href=self._target_,
            external_link=True,
            target="_blank",
            title="Open Page (New Tab)",
            color=self._background_,
            className=f"external bi bi-box-arrow-up-right"
        )

    def group(self) -> list[Component]:
        return [self.button(), self.external()]
