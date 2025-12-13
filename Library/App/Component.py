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

    def button(self, *args, **kwargs) -> Component:
        key = kwargs.pop("key", self._key_)
        color = kwargs.pop("color", self._background_)
        classname = kwargs.pop("className", "button")
        return dbc.Button(
            *args,
            id=key,
            color=color,
            className=classname,
            **kwargs,
        )

    def group(self) -> list[Component]:
        return [self.button(self._label_)]

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

    def group(self) -> list[Component]:
        button = self.button(self._label_, title="Open Page", href=self._target_)
        external = self.button(external_link=True, title="Open Page (New Tab)", href=self._target_, target="_blank", className="external bi bi-box-arrow-up-right")
        return [button, external]
