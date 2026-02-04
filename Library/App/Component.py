from dash import html, dcc
import dash_bootstrap_components as dbc
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from Library.App import TriggerAPI
from Library.Utility import Component

def parse_id(id: dict = None) -> dict:
    return id or {}

def parse_classname(basename: str = None, classname: str = None, stylename: str = None) -> str:
    basename: str = basename or ""
    classname: str = classname or ""
    stylename: str = stylename or ""
    return f"{basename} {classname} {stylename}".strip()

def parse_style(basestyle: dict = None, classstyle: dict = None) -> dict:
    return {**(basestyle or {}), **(classstyle or {})}

@dataclass(kw_only=True)
class ComponentAPI(Component, ABC):

    id: dict = field(default_factory=dict)
    basename: str = field(default="component")
    classname: str = field(default_factory=str)
    stylename: str = field(default_factory=str)
    style: dict = field(default_factory=dict)

    def __post_init__(self):
        self.id = parse_id(id=self.id)
        self.classname = parse_classname(basename=self.basename, classname=self.classname, stylename=self.stylename)
        self.style = parse_style(basestyle=self.style)

    def arguments(self) -> dict:
        kwargs = {}
        if self.id: kwargs.update(id=self.id)
        if self.classname: kwargs.update(className=self.classname)
        if self.style: kwargs.update(style=self.style)
        return kwargs

    @abstractmethod
    def build(self) -> list[Component]:
        raise NotImplementedError

    def __repr__(self):
        return repr(self.build())

@dataclass(kw_only=True)
class ContainerAPI(ComponentAPI, ABC):

    basename: str = field(default="group")
    elements: list[ComponentAPI] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.elements, list): self.elements = self.elements
        elif isinstance(self.elements, ComponentAPI): self.elements = [self.elements]
        else: self.elements = []
        super().__post_init__()

def flatten_components(elements: list[ComponentAPI]) -> list[Component]:
    flat = []
    for element in elements:
        flat.extend(element.build())
    return flat

@dataclass(kw_only=True)
class IconAPI(ComponentAPI):

    classname: str = field(default="icon")
    icon: str = field(default_factory=str)
    text: str = field(default_factory=str)

    def __post_init__(self):
        self.stylename = self.icon
        super().__post_init__()

    def build(self) -> list[Component]:
        return [html.I(**self.arguments(), children=self.text)]

@dataclass(kw_only=True)
class TextAPI(ComponentAPI):

    classname: str = field(default="text")
    icon: str = field(default_factory=str)
    text: str = field(default_factory=str)

    def __post_init__(self):
        self.stylename = self.icon
        super().__post_init__()

    def build(self) -> list[Component]:
        return [html.Span(**self.arguments(), children=self.text)]

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
    href: str = field(default_factory=str)
    external: bool = field(default=False)
    trigger: dict = field(default=None)

    def __post_init__(self):
        if isinstance(self.label, str): self.label = [TextAPI(text=self.label)]
        super().__post_init__()

    def arguments(self) -> dict:
        classstyle = {"border": f"1px solid {self.border}", "border-radius": self.radius}
        self.style = parse_style(basestyle=self.style, classstyle=classstyle)
        kwargs = super().arguments()
        if self.title: kwargs.update(title=self.title)
        if self.clicks: kwargs.update(n_clicks=self.clicks)
        if self.value: kwargs.update(value=self.value)
        if self.disabled: kwargs.update(disabled=self.disabled)
        if self.background: kwargs.update(color=self.background)
        if self.size: kwargs.update(size=self.size)
        if self.href: kwargs.update(href=self.href)
        if self.external: kwargs.update(external_link=self.external, target="_blank")
        return kwargs

    def build(self) -> list[Component]:
        label = flatten_components(elements=self.label)
        button = dbc.Button(label, **self.arguments())
        if not self.trigger: return [button]
        hidden = dcc.Store(id=self.trigger, storage_type="memory", data=TriggerAPI().dict())
        return [button, hidden]

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
        kwargs = super().arguments()
        kwargs.update(size=self.size)
        kwargs.update(vertical=self.vertical)
        return kwargs

    def build(self) -> list[Component]:
        elements = flatten_components(elements=self.elements)
        buttons = [c for c in elements if not isinstance(c, dcc.Store)]
        hidden = [c for c in elements if isinstance(c, dcc.Store)]
        group = dbc.ButtonGroup(buttons, **self.arguments())
        if not hidden: return [group]
        return [group, *hidden]

@dataclass(kw_only=True)
class PaginatorAPI(ButtonContainerAPI):

    classname: str = field(default="paginator")
    iid: dict = field(default_factory=dict)
    eid: dict = field(default_factory=dict)
    label: str | list[ComponentAPI] = field(default_factory=list)
    href: str = field(default_factory=str)
    invert: bool = field(default=False)

    def __post_init__(self):
        internal = ButtonAPI(
            id=self.iid,
            href=self.href,
            title="Open Page",
            external=False,
            label=self.label,
            stylename="internal"
        )
        external = ButtonAPI(
            id=self.eid,
            href=self.href,
            title="Open Page (New Tab)",
            external=True,
            stylename="external bi bi-box-arrow-up-right"
        )
        self.elements = [internal, external] if not self.invert else [external, internal]
        super().__post_init__()
