import dash_bootstrap_components as dbc
from abc import ABC, abstractmethod

from Library.Utility import Component

class ComponentAPI(Component, ABC):

    @abstractmethod
    def build(self, **style) -> Component:
        raise NotImplementedError

    def __repr__(self):
        return repr(self.build())

class ButtonAPI(ComponentAPI):

    def __init__(self,
                 key: dict = None,
                 label: str = None,
                 classname: str = None,
                 background: str = "white",
                 border: str = "black",
                 radius: str = "6px",
                 size: str = "md",
                 vertical: bool = False):
        super().__init__()
        self._key_: dict = key or {}
        self._label_: str = label
        self._background_: str = background
        self._border_: str = border
        self._radius_: str = radius
        self._size_: str = size
        self._vertical_: bool = vertical
        self._classname_: str = classname

    def button(self, *args, **kwargs) -> Component:
        key = kwargs.pop("key", self._key_)
        classname = kwargs.pop("className", self._classname_)
        classname = classname or ""
        return dbc.Button(
            *args,
            id=key,
            color=self._background_,
            className=f"component-button {classname}".strip(),
            **kwargs,
        )

    def group(self) -> list[Component]:
        return [self.button(children=self._label_)]

    def build(self, **style) -> Component:
        return dbc.ButtonGroup(
            children=self.group(),
            size=self._size_,
            vertical=self._vertical_,
            style={"border": f"1px solid {self._border_}", "border-radius": self._radius_, **style},
            className=f"component-button-group"
        )

class PageButtonAPI(ButtonAPI):

    def __init__(self,
                 key: dict = None,
                 label: str = None,
                 target: str = None,
                 classname: str = None,
                 background: str = "white",
                 border: str = "black",
                 radius: str = "6px",
                 size: str = "md",
                 vertical: bool = False):
        super().__init__(
            key=key,
            label=label,
            classname=classname,
            background=background,
            border=border,
            radius=radius,
            size=size,
            vertical=vertical
        )
        self._target_: str = target

    def button(self, *args, **kwargs) -> Component:
        return super().button(*args, href=self._target_, **kwargs)

    def group(self) -> list[Component]:
        internal = self.button(children=self._label_, external_link=False, title="Open Page", target="_self", className=f"internal-button {self._classname_}")
        external = self.button(children=None, external_link=True, title="Open Page (New Tab)", target="_blank", className="external-button bi bi-box-arrow-up-right")
        return [internal, external]

class ButtonMenuAPI(ComponentAPI):

    def __init__(self,
                 keys: list[dict] = None,
                 labels: list[str] = None,
                 classnames: list[str] = None,
                 background: str = "white",
                 border: str = "black",
                 radius: str = "6px",
                 size: str = "md",
                 vertical: bool = False):
        super().__init__()
        if keys is not None: self._n_: int = len(keys)
        elif labels is not None: self._n_: int = len(labels)
        elif classnames is not None: self._n_: int = len(classnames)
        else: self._n_: int = 0
        self._keys_: list[dict] = keys or [None] * self._n_
        self._labels_: list[str] = labels or [None] * self._n_
        self._classnames_: list[str] = classnames or [None] * self._n_
        self._background_: str = background
        self._border_: str = border
        self._radius_: str = radius
        self._size_: str = size
        self._vertical_: bool = vertical

    def menu(self) -> list[ComponentAPI]:
        menu = []
        for key, label, classname in zip(self._keys_, self._labels_, self._classnames_):
            menu.append(ButtonAPI(
                key=key,
                label=label,
                classname=classname,
                background=self._background_,
                border=self._background_,
                radius=self._radius_,
                size=self._size_,
                vertical=self._vertical_
            ))
        return menu

    def build(self, **style) -> Component:
        return dbc.ButtonGroup(
            children=[button.build() for button in self.menu()],
            size=self._size_,
            vertical=self._vertical_,
            style={"border": f"1px solid {self._border_}", "border-radius": self._radius_, **style},
            className="component-button-menu-group"
        )

class PageButtonMenuAPI(ButtonMenuAPI):

    def __init__(self,
                 keys: list[dict] = None,
                 labels: list[str] = None,
                 targets: list[str] = None,
                 classnames: list[str] = None,
                 background: str = "white",
                 border: str = "black",
                 radius: str = "6px",
                 size: str = "md",
                 vertical: bool = False):

        super().__init__(
            keys=keys,
            labels=labels,
            classnames=classnames,
            background=background,
            border=border,
            radius=radius,
            size=size,
            vertical=vertical
        )
        self._targets_: list[str] = targets or [None] * self._n_

    def menu(self) -> list[ComponentAPI]:
        menu = []
        for key, label, target, classname in zip(self._keys_, self._labels_, self._targets_, self._classnames_):
            menu.append(PageButtonAPI(
                key=key,
                label=label,
                target=target,
                classname=classname,
                background=self._background_,
                border=self._background_,
                radius=self._radius_,
                size=self._size_,
                vertical=self._vertical_
            ))
        return menu
