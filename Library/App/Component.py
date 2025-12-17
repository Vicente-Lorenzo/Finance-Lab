from dash import html
import dash_bootstrap_components as dbc
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from Library.Utility import Component

def parse_key(key: dict = None) -> dict:
    return key or {}

def parse_classname(basename: str = None, classname: str = None, instancename: str = None) -> str:
    basename: str = basename or ""
    classname: str = classname or ""
    instancename: str = instancename or ""
    return f"{basename} {classname} {instancename}".strip()

def parse_style(basestyle: dict = None, classstyle: dict = None) -> dict:
    return {**(basestyle or {}), **(classstyle or {})}

@dataclass(kw_only=True)
class ComponentAPI(Component, ABC):

    key: dict = field(default_factory=dict)
    basename: str = field(default="component")
    classname: str = field(default_factory=str)
    instancename: str = field(default_factory=str)
    style: dict = field(default_factory=dict)

    def __post_init__(self):
        self.key = parse_key(key=self.key)
        self.classname = parse_classname(basename=self.basename, classname=self.classname, instancename=self.instancename)
        self.style = parse_style(basestyle=self.style)

    def arguments(self) -> dict:
        return {"id": self.key, "className": self.classname, "style": self.style}

    @abstractmethod
    def build(self) -> Component:
        raise NotImplementedError

@dataclass(kw_only=True)
class ContainerAPI(ComponentAPI, ABC):

    basename: str = field(default="group")
    elements: list[ComponentAPI] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.elements, list): self.elements = self.elements
        elif isinstance(self.elements, ComponentAPI): self.elements = [self.elements]
        else: self.elements = []
        super().__post_init__()

@dataclass(kw_only=True)
class IconAPI(ComponentAPI):

    classname: str = field(default="icon")
    text: str = field(default_factory=str)
    icon: str = field(default_factory=str)

    def __post_init__(self):
        self.instancename = self.icon
        super().__post_init__()

    def build(self) -> Component:
        return html.I(**self.arguments(), children=self.text)

@dataclass(kw_only=True)
class TextAPI(ComponentAPI):

    classname: str = field(default="text")
    text: str = field(default_factory=str)
    icon: str = field(default_factory=str)

    def __post_init__(self):
        self.instancename = self.icon
        super().__post_init__()

    def build(self) -> Component:
        return html.Span(**self.arguments(), children=self.text)

@dataclass(kw_only=True)
class ButtonAPI(ComponentAPI):

    classname: str = field(default="button")
    label: str | list[ComponentAPI] = field(default_factory=list)
    title: str = field(default_factory=str)
    clicks: int = field(default=0)
    value: str = field(default_factory=str)
    disabled: bool = field(default=False)
    background: str = field(default="white")
    border: str = field(default="black")
    radius: str = field(default="6px")
    size: str = field(default="md")
    target: str = field(default_factory=str)
    external: bool = field(default=False)

    def __post_init__(self):
        if isinstance(self.label, str): self.label = [TextAPI(text=self.label)]
        super().__post_init__()

    def arguments(self) -> dict:
        classstyle = {"border": f"1px solid {self.border}", "border-radius": self.radius}
        self.style = parse_style(basestyle=self.style, classstyle=classstyle)
        return {
            **super().arguments(),
            "title": self.title,
            "n_clicks": self.clicks,
            "value": self.value,
            "disabled": self.disabled,
            "color": self.background,
            "size": self.size,
            "href": self.target,
            "external_link": self.external,
            "target": "_blank" if self.external else "_self"
        }

    def build(self) -> Component:
        label = [element.build() for element in self.label]
        return dbc.Button(label, **self.arguments())

@dataclass(kw_only=True)
class IconButtonAPI(ButtonAPI):

    classname: str = field(default="icon-button")
    icon: str = field(default_factory=str)
    text: str = field(default_factory=str)

    def __post_init__(self):
        icon = IconAPI(icon=self.icon)
        text = TextAPI(text=f" {self.text} ")
        self.label = [icon, text, icon]
        super().__post_init__()

@dataclass(kw_only=True)
class ButtonContainerAPI(ContainerAPI):

    classname: str = field(default="buttons")
    background: str = field(default="white")
    border: str = field(default="black")
    radius: str = field(default="6px")
    size: str = field(default="md")
    vertical: bool = field(default=False)
    elements: list[ButtonAPI] = field(default_factory=list)

    def __post_init__(self):
        for button in self.elements:
            button.background = self.background
            button.border = self.background
            button.radius = "auto"
            button.size = self.size
        super().__post_init__()

    def arguments(self) -> dict:
        classstyle = {"border": f"1px solid {self.border}", "border-radius": self.radius}
        self.style = parse_style(basestyle=self.style, classstyle=classstyle)
        return {
            **super().arguments(),
            "size": self.size,
            "vertical": self.vertical
        }

    def build(self) -> Component:
        elements = [element.build() for element in self.elements]
        return dbc.ButtonGroup(elements, **self.arguments())

@dataclass(kw_only=True)
class PaginatorAPI(ButtonContainerAPI):

    classname: str = field(default="paginator")
    label: str = field(default_factory=str)
    target: str = field(default_factory=str)

    def __post_init__(self):
        internal = ButtonAPI(
            target=self.target,
            title="Open Page",
            external=False,
            label=self.label,
            instancename="internal"
        )
        external = ButtonAPI(
            target=self.target,
            title="Open Page (New Tab)",
            external=True,
            instancename="external bi bi-box-arrow-up-right"
        )
        self.elements = [internal, external]
        super().__post_init__()
