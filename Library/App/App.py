import dash
from dash import dcc, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from abc import ABC, abstractmethod
from pathlib import PurePosixPath

from Library.Logging import *
from Library.App import *
from Library.Utility.HTML import *
from Library.Utility.Path import *

class AppAPI(ABC):

    _LAYOUT_ID_: dict = {"type": "div", "index": "app"}
    _HEADER_ID_: dict = {"type": "div", "index": "header"}
    _CONTENT_ID_: dict = {"type": "div", "index": "content"}
    _FOOTER_ID_: dict = {"type": "div", "index": "footer"}
    _HIDDEN_ID_: dict = {"type": "div", "index": "hidden"}

    _PAGE_LOCATION_ID_: dict = {"type": "location", "index": "page"}
    _PAGE_SELECTED_ID_: dict = {"type": "div", "index": "selected"}
    _PAGE_NAVIGATION_ID_: dict = {"type": "div", "index": "navigation"}
    _PAGE_BACKWARD_ID_: dict = {"type": "button", "index": "backward"}
    _PAGE_REFRESH_ID_: dict = {"type": "button", "index": "refresh"}
    _PAGE_FORWARD_ID_: dict = {"type": "button", "index": "forward"}

    _TERMINAL_ARROW_ID_: dict = {"type": "span", "index": "terminal"}
    _TERMINAL_BUTTON_ID_: dict = {"type": "button", "index": "terminal"}
    _TERMINAL_CONTENT_ID_: dict = {"type": "div", "index": "terminal"}
    _TERMINAL_COLLAPSE_ID_: dict = {"type": "collapse", "index": "terminal"}
    _CONTACTS_ARROW_ID_: dict = {"type": "span", "index": "contacts"}
    _CONTACTS_BUTTON_ID_: dict = {"type": "button", "index": "contacts"}
    _CONTACTS_CONTENT_ID_: dict = {"type": "div", "index": "contacts"}
    _CONTACTS_COLLAPSE_ID_: dict = {"type": "collapse", "index": "contacts"}

    INTERVAL_ID: dict = {"type": "interval", "index": "interval"}
    HISTORY_STORAGE_ID: dict = {"type": "storage", "index": "history"}
    SESSION_STORAGE_ID: dict = {"type": "storage", "index": "session"}

    EMPTY_LAYOUT: Component = None
    LOADING_LAYOUT: Component = None
    MAINTENANCE_LAYOUT: Component = None
    DEVELOPMENT_LAYOUT: Component = None

    def __init__(self,
                 name: str = "<Insert App Name>",
                 title: str = "<Insert App Title>",
                 team: str = "<Insert Team Name>",
                 description: str = None,
                 contact: str = "<Insert Contact Email>",
                 update: str = "",
                 protocol: str = None,
                 host: str = None,
                 port: int = None,
                 domain: str = None,
                 proxy: str = None,
                 anchor: str = None,
                 debug: bool = False):

        self._log_: HandlerLoggingAPI = HandlerLoggingAPI(self.__class__.__name__)
        self._pages_: dict[str, PageAPI] = {}

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
        self.update: str = update
        self._log_.debug(lambda: f"Defined Update = {self.update}")

        protocol: str = protocol or "http"
        self.protocol: str = inspect_file_path(protocol, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Protocol = {self.protocol}")
        host: str = host or "localhost"
        self.host: str = inspect_file_path(host, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Host = {self.host}")
        self.port: int = port or 8050
        self._log_.debug(lambda: f"Defined Port = {self.port}")

        host_address: str = f"{self.host}:{self.port}"
        self.host_address: str = inspect_file_path(host_address, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Host Address = {self.host_address}")
        self.host_url: str = f"{self.protocol}://{self.host_address}"
        self._log_.debug(lambda: f"Defined Host URL = {self.host_url}")

        domain_address: str = domain or self.host_address
        self.domain_address: str = inspect_file_path(domain_address, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Domain Address = {self.domain_address}")
        self.domain_url: str = f"{self.protocol}://{self.domain_address}"
        self._log_.debug(lambda: f"Defined Domain URL = {self.domain_url}")

        self.proxy: str = proxy or f"{self.host_url}::{self.domain_url}"
        self._log_.debug(lambda: f"Defined Proxy = {self.proxy}")

        anchor: str = anchor or "/"
        self.anchor: PurePath = inspect_file(anchor, header=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Anchor = {self.anchor}")
        self.endpoint: str = inspect_file_path(anchor, header=True, footer=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Endpoint = {self.endpoint}")

        self.debug: bool = debug
        self._log_.debug(lambda: f"Defined Debug = {self.debug}")

        self.module: PurePath = traceback_current_module(resolve=True)
        self._log_.debug(lambda: f"Defined Calling = {self.module}")
        self.assets: str = inspect_path(self.module / "Assets")
        self._log_.debug(lambda: f"Defined Assets = {self.assets}")

        self._init_app_()
        self._log_.info(lambda: "Initialized App")

        self._init_pages_()
        self._log_.debug(lambda: "Initialized Pages")

        self._init_layouts_()
        self._log_.info(lambda: "Initialized Layout")

        self._init_callbacks_()
        self._log_.info(lambda: "Initialized Callbacks")

    def _init_app_(self):

        self.app = dash.Dash(
            name=self.name,
            title=self.title,
            update_title=self.update,
            assets_folder=self.assets,
            url_base_pathname=self.endpoint,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
            suppress_callback_exceptions=True,
            prevent_initial_callbacks=True
        )

    def _init_pages_(self) -> None:

        self.EMPTY_LAYOUT: Component = DefaultLayoutAPI(
            image=self.app.get_asset_url("404.png"),
            title="Resource Not Found",
            description="Unable to find the resource you are looking for.",
            details="Please check the url path."
        ).build()

        self.LOADING_LAYOUT = DefaultLayoutAPI(
            image=self.app.get_asset_url("loading.gif"),
            title="Loading...",
            description="This resource is loading its content.",
            details="Please wait a moment."
        ).build()

        self.MAINTENANCE_LAYOUT = DefaultLayoutAPI(
            image=self.app.get_asset_url("maintenance.png"),
            title="Resource Under Maintenance",
            description="This resource is temporarily down for maintenance.",
            details="Please try again later."
        ).build()

        self.DEVELOPMENT_LAYOUT = DefaultLayoutAPI(
            image=self.app.get_asset_url("development.png"),
            title="Resource Under Development",
            description="This resource is currently under development.",
            details="Please try again later."
        ).build()

        self.pages()

    def _init_navigation_(self) -> None:

        def new_tab_button(href: str, className: str):
            return html.A(
                dbc.Button(html.I(className="bi bi-box-arrow-up-right"), className=f"{className}-b"),
                href=href,
                target="_blank",
                title="Open in new tab",
                className=f"{className}-a",
            )

        for endpoint, page in self._pages_.items():

            if not page.children and page.parent is not None:
                page.navigation = page.parent.navigation
                continue

            navigation_items: list = []

            if page.parent is not None:
                navigation_items.append(dbc.ButtonGroup(dbc.Button(f"⭰ {page.parent.button}", href=page.parent._anchor_, className="header-navigation-button"), className="header-navigation-group"))

            for child in page.children:
                navigation_group: list = [
                    dbc.Button(child.button, href=child._anchor_, className="header-navigation-button"),
                    new_tab_button(href=child._anchor_, className="header-navigation-button-tab")
                ]
                if child.children:
                    dropdown_group = []
                    for subchild in child.children:
                        dropdown_group.append(dbc.DropdownMenuItem([
                            dbc.Button(subchild.button, href=subchild._anchor_, className="header-navigation-dropdown-button"),
                            new_tab_button(href=subchild._anchor_, className="header-navigation-dropdown-button-tab")
                        ], className="header-navigation-dropdown-group"))
                    navigation_group.append(dbc.DropdownMenu(dropdown_group, direction="down", className="header-navigation-dropdown"))
                navigation_items.append(dbc.ButtonGroup(navigation_group, className="header-navigation-group"))
            page.navigation = dbc.Navbar(navigation_items, className="header-navigation-bar")

    def _init_header_(self) -> html.Div:

        return html.Div([
            html.Div([
                html.Div([html.Img(src=self.app.get_asset_url("logo.png"), className="header-image")], className="header-logo"),
                html.Div([html.H1(self.name, className="header-title"), html.H4(self.team, className="header-team")], className="header-title-team"),
                html.Div([self.description], id=self._PAGE_SELECTED_ID_, className="header-description")
            ], className="header-information-block"),
            html.Div([
                html.Div(None, id=self._PAGE_NAVIGATION_ID_, className="header-navigation-block"),
                html.Div(ButtonMenuAPI(
                    keys=[self._PAGE_BACKWARD_ID_, self._PAGE_REFRESH_ID_, self._PAGE_FORWARD_ID_],
                    classnames=["bi bi-arrow-left", "bi bi-arrow-repeat", "bi bi-arrow-right"]
                ).build(), className="header-history-block")
            ], className="header-control-block")
        ], id=self._HEADER_ID_, className="header")

    def _init_content_(self) -> html.Div:

        return html.Div([
            self.LOADING_LAYOUT
        ], id=self._CONTENT_ID_, className="content")

    def _init_contacts_(self) -> html.Div:

        return html.Div([
            html.Div([html.B("Team: "), html.Span(self.team)]),
            html.Div([html.B("Contact: "), html.A(self.contact, href=f"mailto:{self.contact}")])
        ])

    def _init_footer_(self) -> html.Div:
        return html.Div([
            dbc.Button([html.Span("▼", id=self._CONTACTS_ARROW_ID_), " Contacts ", html.I(className="bi bi-question-circle")], id=self._CONTACTS_BUTTON_ID_, color="primary", className="footer-button"),
            dbc.Button([html.I(className="bi bi-terminal"), " Terminal ", html.Span("▼", id=self._TERMINAL_ARROW_ID_)], id=self._TERMINAL_BUTTON_ID_, color="primary", className="footer-button"),
            dbc.Collapse(dbc.Card(dbc.CardBody(html.Div(self._init_contacts_(), id=self._CONTACTS_CONTENT_ID_)), className="footer-panel footer-panel-left"), id=self._CONTACTS_COLLAPSE_ID_, is_open=False),
            dbc.Collapse(dbc.Card(dbc.CardBody(html.Pre([], id=self._TERMINAL_CONTENT_ID_)), color="dark", inverse=True, className="footer-panel footer-panel-right"), id=self._TERMINAL_COLLAPSE_ID_, is_open=False)
        ], id=self._FOOTER_ID_, className="footer")

    def _init_hidden_(self) -> html.Div:

        return html.Div([
            dcc.Interval(id=self.INTERVAL_ID, interval=1000, n_intervals=0, disabled=False),
            dcc.Store(id=self.HISTORY_STORAGE_ID, storage_type="session", data=HistorySessionAPI().dict()),
            dcc.Store(id=self.SESSION_STORAGE_ID, storage_type="session"),
            dcc.Location(id=self._PAGE_LOCATION_ID_, refresh=False)
        ], id=self._HIDDEN_ID_)

    def _init_layouts_(self):

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
            id=self._LAYOUT_ID_,
            className="app"
        )

    def _init_callbacks_(self):

        @self.app.callback(
            dash.Output(self._PAGE_LOCATION_ID_, "pathname", allow_duplicate=True),
            dash.Output(self._PAGE_SELECTED_ID_, "children", allow_duplicate=True),
            dash.Output(self._PAGE_NAVIGATION_ID_, "children", allow_duplicate=True),
            dash.Output(self._CONTENT_ID_, "children", allow_duplicate=True),
            dash.Input(self._PAGE_LOCATION_ID_, "pathname"),
            prevent_initial_call=False
        )
        def _update_location_callback_(path: str):
            self._log_.debug(lambda: f"Location Callback: Received Path = {path}")
            anchor = self.anchorize(path=path)
            self._log_.debug(lambda: f"Location Callback: Parsed Anchor = {anchor}")
            endpoint = self.endpointize(path=path)
            self._log_.debug(lambda: f"Location Callback: Parsed Endpoint = {endpoint}")
            page = self.locate(endpoint=endpoint)
            if page is not None:
                self._log_.debug(lambda: f"Location Callback: Page Found")
                description = page.description if not self.description and page.description else dash.no_update
                navigation = page.navigation if page.navigation else dash.no_update
                content = page.layout
            else:
                self._log_.debug(lambda: f"Location Callback: Page Not Found")
                description = dash.no_update
                navigation = dash.no_update
                content = self.EMPTY_LAYOUT
            return anchor, description, navigation, content

        @self.app.callback(
            dash.Output(self.HISTORY_STORAGE_ID, "data", allow_duplicate=True),
            dash.Input(self._PAGE_LOCATION_ID_, "pathname"),
            dash.State(self.HISTORY_STORAGE_ID, "data"),
            prevent_initial_call=True
        )
        def _update_history_callback_(path, history):
            history = HistorySessionAPI(**history)
            history.Register(path)
            return history.dict()

        @self.app.callback(
            dash.Output(self._PAGE_LOCATION_ID_, "pathname", allow_duplicate=True),
            dash.Input(self._PAGE_BACKWARD_ID_, "n_clicks"),
            dash.State(self.HISTORY_STORAGE_ID, "data"),
            prevent_initial_call=True
        )
        def _backward_history_callback_(clicks, history):
            if clicks is None: raise PreventUpdate
            history = HistorySessionAPI(**history)
            path = history.Backward()
            return path if path else dash.no_update

        @self.app.callback(
            dash.Output(self._PAGE_LOCATION_ID_, "pathname", allow_duplicate=True),
            dash.Input(self._PAGE_REFRESH_ID_, "n_clicks"),
            dash.State(self._PAGE_LOCATION_ID_, "pathname"),
            prevent_initial_call=True
        )
        def _refresh_history_callback_(clicks, path):
            if clicks is None: raise PreventUpdate
            return path

        @self.app.callback(
            dash.Output(self._PAGE_LOCATION_ID_, "pathname", allow_duplicate=True),
            dash.Input(self._PAGE_FORWARD_ID_, "n_clicks"),
            dash.State(self.HISTORY_STORAGE_ID, "data"),
            prevent_initial_call=True
        )
        def _forward_history_callback_(clicks, history):
            if clicks is None: raise PreventUpdate
            history = HistorySessionAPI(**history)
            path = history.Forward()
            return path if path else dash.no_update

        def _collapsable_button_callback_(was_open: bool):
            is_open = not was_open
            arrow = "▲" if is_open else "▼"
            return arrow, is_open

        @self.app.callback(
            dash.Output(self._CONTACTS_ARROW_ID_, "children", allow_duplicate=True),
            dash.Output(self._CONTACTS_COLLAPSE_ID_, "is_open", allow_duplicate=True),
            dash.Input(self._CONTACTS_BUTTON_ID_, "n_clicks"),
            dash.State(self._CONTACTS_COLLAPSE_ID_, "is_open"),
            prevent_initial_call=True
        )
        def _contacts_button_callback_(clicks, was_open: bool):
            if clicks is None: raise PreventUpdate
            arrow, is_open = _collapsable_button_callback_(was_open)
            self._log_.debug(lambda: f"Contacts Callback: {'Expanding' if is_open else 'Collapsing'}")
            return arrow, is_open

        @self.app.callback(
            dash.Output(self._TERMINAL_ARROW_ID_, "children", allow_duplicate=True),
            dash.Output(self._TERMINAL_COLLAPSE_ID_, "is_open", allow_duplicate=True),
            dash.Input(self._TERMINAL_BUTTON_ID_, "n_clicks"),
            dash.State(self._TERMINAL_COLLAPSE_ID_, "is_open"),
            prevent_initial_call=True
        )
        def _terminal_button_callback_(clicks, was_open: bool):
            if clicks is None: raise PreventUpdate
            arrow, is_open = _collapsable_button_callback_(was_open)
            self._log_.debug(lambda: f"Terminal Callback: {'Expanding' if is_open else 'Collapsing'}")
            return arrow, is_open

        @self.app.callback(
            dash.Output(self._TERMINAL_CONTENT_ID_, "children", allow_duplicate=True),
            dash.Input(self.INTERVAL_ID, "n_intervals"),
            dash.State(self._TERMINAL_CONTENT_ID_, "children"),
            prevent_initial_call=True
        )
        def _terminal_stream_callback_(_, terminal):
            logs = self._log_.web.stream()
            if not logs: raise PreventUpdate
            terminal.extend(logs)
            return terminal

        # self.callbacks()

    def resolve(self, path: str | PurePath, footer: bool = None) -> str:
        path: str = inspect_path(path) if isinstance(path, PurePath) else path
        self._log_.debug(lambda: f"Resolve Path: Received = {path}")
        path: str = inspect_file_path(path, header=False, builder=PurePosixPath)
        self._log_.debug(lambda: f"Resolve Path: Parsed = {path}")
        resolve: str = inspect_path(self.anchor / path, footer=footer)
        self._log_.debug(lambda: f"Resolve Path: Resolved = {resolve}")
        return resolve

    def anchorize(self, path: str | PurePath):
        return self.resolve(path, footer=False)

    def endpointize(self, path: str | PurePath):
        return self.resolve(path, footer=True)

    def locate(self, endpoint: str) -> PageAPI | None:
        return self._pages_.get(endpoint, None)

    """
    def link(self, page: PageAPI):
        alias: PurePath | None = None
        node: PageAPI | None = None
        path: PurePath = inspect_file(page.path, header=True, builder=PurePosixPath)
        for name in path.parts:
            self._log_.debug(lambda: f"Page Linking: Name = {name}")
            name = inspect_file(name, header=True, builder=PurePosixPath).name
            alias = self.anchor / alias / name if alias is not None else self.anchor / name
            self._log_.debug(lambda: f"Page Linking: Alias = {alias}")
            anchor = inspect_path(alias)
            self._log_.debug(lambda: f"Page Linking: Anchor = {anchor}")
            endpoint = inspect_path(alias, footer=True)
            self._log_.debug(lambda: f"Page Linking: Endpoint = {endpoint}")
            if endpoint not in self._pages_:
                self._log_.debug(lambda: "Page Linking: Not Found")
                new = PageAPI(
                    app=self,
                    path=inspect_path(alias),
                    anchor=anchor,
                    endpoint=endpoint,
                    indexed=False
                )
                new.parent = node
                if node:
                    self._log_.debug(lambda: f"Page Linking: Parent = {node._anchor_}")
                    self._log_.debug(lambda: f"Page Linking: Family = {len(node.family)}")
                self._pages_[endpoint] = new
            else:
                self._log_.debug(lambda: "Page Linking: Found")
                new = self._pages_[endpoint]
            node = new
        self._pages_[page._endpoint_] = page
        self._log_.info(lambda: f"Defined Link: Endpoint = {node._endpoint_}")
    """

    def link(self, page: PageAPI):
        relative_path: PurePath = inspect_file(page.path, header=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Page Linking: Relative Path = {relative_path}")
        relative_anchor = self.anchorize(path=relative_path)
        self._log_.debug(lambda: f"Page Linking: Relative Anchor = {relative_anchor}")
        relative_endpoint = self.endpointize(path=relative_path)
        self._log_.debug(lambda: f"Page Linking: Relative Endpoint = {relative_endpoint}")
        intermediate_alias: PurePath = inspect_file("/", builder=PurePosixPath)
        for part in relative_path.parts[1:-1]:
            intermediate_path: PurePath = inspect_file(part, header=True, builder=PurePosixPath)
            intermediate_alias = intermediate_alias / intermediate_path.name
            self._log_.debug(lambda: f"Page Linking: Intermediate Path = {intermediate_alias}")
            intermediate_anchor = self.anchorize(path=intermediate_alias)
            self._log_.debug(lambda: f"Page Linking: Intermediate Anchor = {intermediate_anchor}")
            intermediate_endpoint = self.endpointize(path=intermediate_alias)
            self._log_.debug(lambda: f"Page Linking: Intermediate Endpoint = {intermediate_endpoint}")
            intermediate_page: PageAPI = self.locate(endpoint=intermediate_endpoint)
        page.anchor = relative_anchor
        page.endpoint = relative_endpoint
        self._pages_[page._endpoint_] = page
        self._log_.info(lambda: f"Page Linking: Defined Page = {page}")

    @abstractmethod
    def pages(self):
        raise NotImplementedError

    def run(self):
        return self.app.run(
            host=self.host,
            port=self.port,
            proxy=self.proxy,
            debug=self.debug,
            jupyter_mode="external",
            jupyter_server_url=self.domain_url
        )
