import dash
from typing import Self
from dash import dcc, html
import dash_bootstrap_components as dbc
from pathlib import PurePath, PurePosixPath
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from Library.Logging import HandlerAPI
from Library.Utility import inspect_file, inspect_path, inspect_file_path, traceback_calling_module

@dataclass(slots=True)
class Link:
    Order: int = field(init=True, default=None)
    Button: str = field(init=True, default=None)
    Description: str = field(init=True, default=None)
    Anchor: str = field(init=True, default=None)
    Endpoint: str = field(init=True, default=None)
    Parent: Self = field(init=True, default=None)
    Children: list[Self] = field(init=True, default_factory=list)
    Layout: html.Div = field(init=True, default=None)
    Navigation: dbc.Navbar = field(init=True, default=None)
    Hidden: bool = field(init=True, default=False)

class AppAPI(ABC):

    LAYOUT_ID: dict = {"type": "div", "index": "layout"}
    HEADER_ID: dict = {"type": "div", "index": "header"}
    CONTENT_ID: dict = {"type": "div", "index": "content"}
    FOOTER_ID: dict = {"type": "div", "index": "footer"}
    HIDDEN_ID: dict = {"type": "div", "index": "hidden"}

    INFORMATION_ID: dict = {"type": "div", "index": "information"}
    LOCATION_ID: dict = {"type": "location", "index": "page"}
    SELECTED_ID: dict = {"type": "div", "index": "selected"}
    NAVIGATION_ID: dict = {"type": "div", "index": "navigation"}
    INTERVAL_ID: dict = {"type": "interval", "index": "interval"}
    SESSION_ID: dict = {"type": "storage", "index": "session"}

    EMPTY_LAYOUT: html.Div = None
    LOADING_LAYOUT: html.Div = None
    DEVELOPMENT_LAYOUT: html.Div = None
    MAINTENANCE_LAYOUT: html.Div = None

    def __init__(self,
                 name: str = "<Insert App Name>",
                 title: str = "<Insert App Title>",
                 team: str = "<Insert Team Name>",
                 description: str = None,
                 contact: str = None,
                 anchor: str = "/",
                 port: int = 8050,
                 debug: bool = False):

        self._log_: HandlerAPI = HandlerAPI()
        self._links_: dict[str, Link] = {}

        self.name: str = name
        self._log_.debug(lambda: f"Defined Name = {self.name}")
        self.title: str = title
        self._log_.debug(lambda: f"Defined Title = {self.title}")
        self.team: str = team
        self._log_.debug(lambda: f"Defined Team = {self.team}")
        self.description: str = description
        self._log_.debug(lambda: f"Defined Description = {self.description}")
        self.contact: str = contact
        self._log_.debug(lambda: f"Defined Contact = {self.contact}")
        self.port: int = port
        self._log_.debug(lambda: f"Defined Port = {self.port}")
        self.debug: bool = debug
        self._log_.debug(lambda: f"Defined Debug = {self.debug}")

        self.anchor: PurePath = inspect_file(anchor, header=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Anchor = {self.anchor}")
        self.endpoint: str = inspect_file_path(anchor, header=True, footer=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Endpoint = {self.endpoint}")

        self.module: PurePath = traceback_calling_module(resolve=True)
        self._log_.debug(lambda: f"Defined Calling = {self.module}")
        self.assets: str = inspect_path(self.module / "Assets")
        self._log_.debug(lambda: f"Defined Assets = {self.assets}")

        self._init_app()
        self._log_.info(lambda: "Initialized App")

        self._init_layouts_()
        self._log_.info(lambda: "Initialized Layout")

        self._init_callbacks_()
        self._log_.info(lambda: "Initialized Callbacks")

    def _init_app(self):

        self.app = dash.Dash(
            name=self.name,
            title=self.title,
            assets_folder=self.assets,
            url_base_pathname=self.endpoint,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
            suppress_callback_exceptions=True,
            prevent_initial_callbacks=True
        )

    def _init_links_(self) -> None:

        self.EMPTY_LAYOUT = html.Div([
            html.Img(src=self.app.get_asset_url("404.png"), className="status-layout-image", alt="Resource Not Found"),
            html.H2("Resource Not Found", className="status-layout-title"),
            html.P("Unable to find the resource you are looking for.", className="status-layout-text"),
            html.P("Please check the url path.", className="status-layout-text"),
        ], className="status-layout status-layout-empty")

        self.LOADING_LAYOUT = html.Div([
            html.Img(src=self.app.get_asset_url("loading.gif"), className="status-layout-image", alt="Loading"),
            html.H2("Loading...", className="status-layout-title"),
            html.P("Please wait a moment.", className="status-layout-text"),
        ], className="status-layout status-layout-loading")

        self.MAINTENANCE_LAYOUT = html.Div([
            html.Img(src=self.app.get_asset_url("maintenance.png"), className="status-layout-image", alt="Under Maintenance"),
            html.H2("Resource Under Maintenance", className="status-layout-title"),
            html.P("This resource is temporarily down for maintenance.", className="status-layout-text"),
            html.P("Please try again later.", className="status-layout-text"),
        ], className="status-layout status-layout-maintenance")

        self.DEVELOPMENT_LAYOUT = html.Div([
            html.Img(src=self.app.get_asset_url("development.png"), className="status-layout-image", alt="Work in Progress"),
            html.H2("Resource Under Development", className="status-layout-title"),
            html.P("This resource is currently under development.", className="status-layout-text"),
            html.P("Please try again later.", className="status-layout-text"),
        ], className="status-layout status-layout-development")

    def _init_selections_(self) -> None:

        def new_tab_button(href: str, className: str):
            return html.A(
                dbc.Button(html.I(className="bi bi-box-arrow-up-right"), className=f"{className}-b"),
                href=href,
                target="_blank",
                title="Open in new tab",
                className=f"{className}-a",
            )

        for endpoint, link in self._links_.items():
            if not link.Children and link.Parent is not None:
                link.Navigation = link.Parent.Navigation
                continue
            items: list = []
            if link.Parent is not None:
                items.append(dbc.ButtonGroup(dbc.Button("⭰ Back", href=link.Parent.Endpoint, className="header-navigation-button"), className="header-navigation-group"))
            for child in link.Children:
                item_group: list = [dbc.Button(child.Button, href=child.Endpoint, className="header-navigation-button"), new_tab_button(href=child.Endpoint, className="header-navigation-button-tab")]
                if child.Children:
                    dropdown_group = []
                    for subchild in child.Children:
                        dropdown_group.append(dbc.DropdownMenuItem([
                            dbc.Button(subchild.Button, href=subchild.Endpoint, className="header-navigation-dropdown-button"),
                            new_tab_button(href=subchild.Endpoint, className="header-navigation-dropdown-button-tab")
                        ], className="header-navigation-dropdown-group"),)
                    item_group.append(dbc.DropdownMenu(dropdown_group, direction="down", className="header-navigation-dropdown"))
                items.append(dbc.ButtonGroup(item_group, className="header-navigation-group"))
            link.Navigation = dbc.Navbar(items, className="header-navigation-bar")

    def _init_header_(self) -> html.Div:

        return html.Div([
            html.Div([
                html.Div([html.Img(src=self.app.get_asset_url("logo.png"), className="header-image")], className="header-logo"),
                html.Div([html.H1(self.name, className="header-title"), html.H4(self.team, className="header-team")], className="header-title-team"),
                html.Div(self.description, id=self.SELECTED_ID, className="header-description")
            ], id=self.INFORMATION_ID, className="header-information-block"),
            html.Div(None, id=self.NAVIGATION_ID, className="header-navigation-block")
        ], id=self.HEADER_ID, className="header")

    def _init_content_(self) -> html.Div:

        return html.Div([
            self.LOADING_LAYOUT
        ], id=self.CONTENT_ID, className="content")

    def _init_footer_(self) -> html.Div:

        return html.Div([
            html.A(
                f"Contact: {self.contact}",
                href=f"mailto:{self.contact}",
                className="footer-contact"
            )
        ], id=self.FOOTER_ID, className="footer")

    def _init_hidden_(self) -> html.Div:

        return html.Div([
            dcc.Interval(id=self.INTERVAL_ID, interval=1000, n_intervals=0, disabled=False),
            dcc.Store(id=self.SESSION_ID, storage_type="memory"),
            dcc.Location(id=self.LOCATION_ID, refresh=False)
        ], id=self.HIDDEN_ID)

    def _init_layouts_(self):

        self._init_links_()
        self._log_.debug(lambda: "Loaded Links Layout")
        self.layout()
        self._log_.debug(lambda: "Loaded Specific Layout")
        self._init_selections_()
        self._log_.debug(lambda: "Loaded Selection Layouts")
        header = self._init_header_()
        self._log_.debug(lambda: "Loaded Header Layout")
        content = self._init_content_()
        self._log_.debug(lambda: "Loaded Content Layout")
        footer = self._init_footer_()
        self._log_.debug(lambda: "Loaded Footer Layout")
        hidden = self._init_hidden_()
        self._log_.debug(lambda: "Loaded Hidden Layout")

        self.app.layout = html.Div(
            [header, content, footer, hidden],
            id=self.LAYOUT_ID,
            className="app"
        )

    def _init_callbacks_(self):

        @self.app.callback(
            dash.Output(self.LOCATION_ID, "pathname", allow_duplicate=True),
            dash.Output(self.SELECTED_ID, "children", allow_duplicate=True),
            dash.Output(self.NAVIGATION_ID, "children", allow_duplicate=True),
            dash.Output(self.CONTENT_ID, "children", allow_duplicate=True),
            dash.Input(self.LOCATION_ID, "pathname")
        )
        def _location_callback_(path: str):
            self._log_.debug(lambda: f"Location Callback: Received Path = {path}")
            endpoint = inspect_file_path(path, header=True, footer=True, builder=PurePosixPath)
            self._log_.debug(lambda: f"Location Callback: Parsed Endpoint = {endpoint}")
            link = self._links_.get(endpoint, None)
            if link is not None:
                self._log_.debug(lambda: f"Location Callback: Link Found")
                description = link.Description if not self.description else dash.no_update
                selection = link.Navigation if link.Navigation else dash.no_update
                layout = link.Layout if link.Layout else self.DEVELOPMENT_LAYOUT
            else:
                self._log_.debug(lambda: f"Location Callback: Link Not Found")
                description = dash.no_update
                selection = dash.no_update
                layout = self.EMPTY_LAYOUT
            return endpoint, description, selection, layout

        self.callbacks()

    def link(self, path: str, button: str, description: str, layout):
        alias: PurePath | None = None
        parent: Link | None = None
        for name in inspect_file(path, header=True, builder=PurePosixPath).parts:
            self._log_.debug(lambda: f"Link Definition: Name = {name}")
            name = inspect_file(name, header=True, builder=PurePosixPath).name
            alias = self.anchor / alias / name if alias is not None else self.anchor / name
            self._log_.debug(lambda: f"Link Definition: Alias = {alias}")
            anchor = inspect_path(alias)
            self._log_.debug(lambda: f"Link Definition: Anchor = {anchor}")
            endpoint = inspect_path(alias, footer=True)
            self._log_.debug(lambda: f"Link Definition: Endpoint = {endpoint}")
            if endpoint not in self._links_:
                self._log_.debug(lambda: "Link Definition: Not Found")
                link = Link()
                link.Anchor = anchor
                link.Endpoint = endpoint
                if parent is not None:
                    link.Parent = parent
                    self._log_.debug(lambda: f"Link Definition: Parent = {parent.Endpoint}")
                    parent.Children.append(link)
                    link.Order = (order := len(parent.Children))
                    self._log_.debug(lambda: f"Link Definition: Order = {order}")
                self._links_[endpoint] = link
            else:
                self._log_.debug(lambda: "Link Definition: Found")
                link = self._links_[endpoint]
            parent = link
        parent.Button = button
        parent.Description = description
        parent.Layout = layout
        self._log_.info(lambda: f"Defined Link: Endpoint = {parent.Endpoint}")

    @abstractmethod
    def layout(self):
        raise NotImplementedError

    @abstractmethod
    def callbacks(self):
        raise NotImplementedError

    def run(self):
        return self.app.run(port=self.port, debug=self.debug)
