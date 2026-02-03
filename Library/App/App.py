import dash
from dash import dcc, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from pathlib import PurePosixPath

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from Library.App import *
from Library.Logging import *
from Library.Utility.HTML import *
from Library.Utility.Path import *
from Library.Utility.Typing import *
from Library.Utility.Runtime import *

class AppAPI:

    _DESCRIPTION_ID_: dict
    _CONTENT_ID_: dict
    _SIDEBAR_BUTTON_ID_: dict
    _SIDEBAR_COLLAPSE_ID_: dict
    _SIDEBAR_ID_: dict

    _LOCATION_ID_: dict
    _BACKWARD_BUTTON_ID_: dict
    _BACKWARD_TRIGGER_ID_: dict
    _REFRESH_BUTTON_ID_: dict
    _REFRESH_TRIGGER_ID_: dict
    _FORWARD_BUTTON_ID_: dict
    _FORWARD_TRIGGER_ID_: dict
    _LOCATION_STORAGE_ID_: dict

    _NAVIGATION_ID_: dict
    NAVIGATION_STORAGE_ID: dict

    _CONTACTS_ARROW_ID_: dict
    _CONTACTS_BUTTON_ID_: dict
    _CONTACTS_COLLAPSE_ID_: dict
    _CONTACTS_ID_: dict

    _TERMINAL_ARROW_ID_: dict
    _TERMINAL_BUTTON_ID_: dict
    _TERMINAL_COLLAPSE_ID_: dict
    _TERMINAL_ID_: dict

    _CLEAN_CACHE_BUTTON_ID_: dict
    _CLEAN_DATA_BUTTON_ID_: dict

    CALLBACK_SINK_ID: dict

    INTERVAL_ID: dict
    MEMORY_STORAGE_ID: dict
    SESSION_STORAGE_ID: dict
    LOCAL_STORAGE_ID: dict

    NOT_FOUND_LAYOUT: Component
    LOADING_LAYOUT: Component
    MAINTENANCE_LAYOUT: Component
    DEVELOPMENT_LAYOUT: Component
    NOT_INDEXED_LAYOUT: Component

    def __init__(self, *,
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
                 debug: bool = False,
                 terminal: int = 1000) -> None:

        self._log_: HandlerLoggingAPI = HandlerLoggingAPI(AppAPI.__name__)
        self._ids_: set = set()
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

        host: str = host or "localhost"
        self.host: str = inspect_file_path(host, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Host = {self.host}")
        self.port: int = port or find_host_port(host=self.host, port_min=8050)
        self._log_.debug(lambda: f"Defined Port = {self.port}")

        protocol: str = protocol or "http"
        self.protocol: str = inspect_file_path(protocol, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Protocol = {self.protocol}")

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
        self.terminal: int = terminal
        self._log_.debug(lambda: f"Defined Terminal = {self.terminal}")

        self.module: PurePath = traceback_current_module(resolve=True)
        self._log_.debug(lambda: f"Defined Calling = {self.module}")
        self.assets: str = inspect_path(self.module / "Assets")
        self._log_.debug(lambda: f"Defined Assets = {self.assets}")

        self._init_ids_()
        self._log_.debug(lambda: "Initialized IDs")

        self._init_app_()
        self._log_.info(lambda: "Initialized App")

        self._init_pages_()
        self._log_.debug(lambda: "Initialized Pages")

        self._init_navigation_()
        self._log_.debug(lambda: "Initialized Navigation")

        self._init_layout_()
        self._log_.info(lambda: "Initialized Layout")

        self._init_callbacks_()
        self._log_.info(lambda: "Initialized Callbacks")

    def identify(self, *, page: str = "global", type: str, name: str) -> dict:
        return {"app": self.__class__.__name__, "page": page, "type": type, "name": name}

    def register(self, *, page: str = "global", type: str, name: str) -> dict:
        cid = self.identify(page=page, type=type, name=name)
        key = (cid["app"], cid["page"], cid["type"], cid["name"])
        if key in self._ids_: raise RuntimeError(f"Duplicate Dash ID detected: {cid}")
        self._ids_.add(key)
        return cid

    def resolve(self, path: PurePath | str, relative: bool, footer: bool = None) -> str:
        path: PurePath = inspect_file(path, header=False, builder=PurePosixPath)
        self._log_.debug(lambda: f"Resolve Path: Received = {path}")
        path: PurePath = self.anchor / path if relative else path
        resolve: str = inspect_file_path(path, header=True, footer=footer, builder=PurePosixPath)
        self._log_.debug(lambda: f"Resolve Path: Resolved = {resolve}")
        return resolve

    def anchorize(self, path: PurePath | str, relative: bool = True) -> str:
        return self.resolve(path, relative=relative, footer=False)

    def endpointize(self, path: PurePath | str, relative: bool = True) -> str:
        return self.resolve(path, relative=relative, footer=True)

    def locate(self, endpoint: str) -> PageAPI | None:
        return self._pages_.get(endpoint, None)

    def index(self, endpoint: str, page: PageAPI) -> None:
        self._pages_[endpoint] = page

    def link(self, page: PageAPI) -> None:
        relative_path: PurePath = inspect_file(page.path, header=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Page Linking: Relative Path = {relative_path}")
        relative_anchor = self.anchorize(path=relative_path, relative=True)
        self._log_.debug(lambda: f"Page Linking: Relative Anchor = {relative_anchor}")
        relative_endpoint = self.endpointize(path=relative_path, relative=True)
        self._log_.debug(lambda: f"Page Linking: Relative Endpoint = {relative_endpoint}")
        intermediate_alias: PurePath = inspect_file("/", builder=PurePosixPath)
        intermediate_parent: PageAPI = self.locate(endpoint=self.endpointize(path=intermediate_alias, relative=True))
        for part in relative_path.parts[1:-1]:
            intermediate_path: PurePath = inspect_file(part, header=True, builder=PurePosixPath)
            intermediate_alias /= intermediate_path.name
            self._log_.debug(lambda: f"Page Linking: Intermediate Path = {intermediate_alias}")
            intermediate_anchor = self.anchorize(path=intermediate_alias, relative=True)
            self._log_.debug(lambda: f"Page Linking: Intermediate Anchor = {intermediate_anchor}")
            intermediate_endpoint = self.endpointize(path=intermediate_alias, relative=True)
            self._log_.debug(lambda: f"Page Linking: Intermediate Endpoint = {intermediate_endpoint}")
            intermediate_page: PageAPI = self.locate(endpoint=intermediate_endpoint)
            if not intermediate_page:
                intermediate_page = PageAPI(
                    app=self,
                    path=inspect_path(intermediate_alias),
                    description="Resource Not Indexed",
                    indexed=False
                )
                self._log_.debug(lambda: f"Page Linking: Created Intermediate Page = {intermediate_endpoint}")
            intermediate_page.anchor = intermediate_anchor
            intermediate_page.endpoint = intermediate_endpoint
            intermediate_page._init_()
            self.index(endpoint=intermediate_page.endpoint, page=intermediate_page)
            self._log_.debug(lambda: f"Page Linking: Linked Intermediate Page = {intermediate_endpoint}")
            intermediate_page.attach(parent=intermediate_parent)
            intermediate_parent = intermediate_page
        page.anchor = relative_anchor
        page.endpoint = relative_endpoint
        existing = self.locate(endpoint=relative_endpoint)
        if existing:
            page.merge(existing)
            self._log_.debug(lambda: f"Page Linking: Merged Relative Page = {relative_endpoint}")
        else:
            self.index(endpoint=page.endpoint, page=page)
            self._log_.info(lambda: f"Page Linking: Linked {page}")
        page.attach(parent=intermediate_parent)
        page._init_()

    def _init_ids_(self) -> None:
        self._DESCRIPTION_ID_: dict = self.register(type="div", name="description")
        self._CONTENT_ID_: dict = self.register(type="div", name="content")
        self._SIDEBAR_BUTTON_ID_: dict = self.register(type="button", name="sidebar")
        self._SIDEBAR_COLLAPSE_ID_: dict = self.register(type="collapse", name="sidebar")
        self._SIDEBAR_ID_: dict = self.register(type="div", name="sidebar")
        self._LOCATION_ID_: dict = self.register(type="location", name="location")
        self._BACKWARD_BUTTON_ID_: dict = self.register(type="button", name="backward-button")
        self._BACKWARD_TRIGGER_ID_ = self.register(type="storage", name="backward-trigger")
        self._REFRESH_BUTTON_ID_: dict = self.register(type="button", name="refresh-button")
        self._REFRESH_TRIGGER_ID_ = self.register(type="storage", name="refresh-trigger")
        self._FORWARD_BUTTON_ID_: dict = self.register(type="button", name="forward-button")
        self._FORWARD_TRIGGER_ID_ = self.register(type="storage", name="forward-trigger")
        self._LOCATION_STORAGE_ID_: dict = self.register(type="storage", name="location")
        self._NAVIGATION_ID_: dict = self.register(type="div", name="navigation")
        self.NAVIGATION_STORAGE_ID: dict = self.register(type="storage", name="navigation")
        self._CONTACTS_ARROW_ID_: dict = self.register(type="icon", name="contacts")
        self._CONTACTS_BUTTON_ID_: dict = self.register(type="button", name="contacts")
        self._CONTACTS_COLLAPSE_ID_: dict = self.register(type="collapse", name="contacts")
        self._CONTACTS_ID_: dict = self.register(type="card", name="contacts")
        self._TERMINAL_ARROW_ID_: dict = self.register(type="icon", name="terminal")
        self._TERMINAL_BUTTON_ID_: dict = self.register(type="button", name="terminal")
        self._TERMINAL_COLLAPSE_ID_: dict = self.register(type="collapse", name="terminal")
        self._TERMINAL_ID_: dict = self.register(type="card", name="terminal")
        self._CLEAN_CACHE_BUTTON_ID_: dict = self.register(type="button", name="clean")
        self._CLEAN_DATA_BUTTON_ID_: dict = self.register(type="button", name="reset")
        self.CALLBACK_SINK_ID: dict = self.register(type="div", name="sink")
        self.INTERVAL_ID: dict = self.register(type="interval", name="1000ms")
        self.MEMORY_STORAGE_ID: dict = self.register(type="storage", name="memory")
        self.SESSION_STORAGE_ID: dict = self.register(type="storage", name="session")
        self.LOCAL_STORAGE_ID: dict = self.register(type="storage", name="local")
        self.ids()

    def _init_app_(self) -> None:
        self.app = dash.Dash(
            name=self.name,
            title=self.title,
            update_title=self.update,
            assets_folder=self.assets,
            routes_pathname_prefix=self.endpoint,
            requests_pathname_prefix=self.endpoint,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
            suppress_callback_exceptions=True,
            prevent_initial_callbacks=True
        )

    def _init_pages_(self) -> None:
        self.NOT_FOUND_LAYOUT = DefaultLayoutAPI(
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
        self.NOT_INDEXED_LAYOUT = DefaultLayoutAPI(
            image=self.app.get_asset_url("indexed.png"),
            title="Resource Not Indexed",
            description="This resource is not indexed at any page.",
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
                page._navigation_ = page.parent._navigation_
                continue

            navigation_items: list = []

            if page.parent is not None:
                navigation_items.append(dbc.ButtonGroup(dbc.Button(f"⭰ {page.parent.button}", href=page.parent.anchor, className="header-navigation-button"), className="header-navigation-group"))

            for member in page.family:
                navigation_group: list = [
                    dbc.Button(member.button, href=member.anchor, className="header-navigation-button"),
                    new_tab_button(href=member.anchor, className="header-navigation-button-tab")
                ]
                if member.children:
                    dropdown_group = []
                    for subchild in member.children:
                        dropdown_group.append(dbc.DropdownMenuItem([
                            dbc.Button(subchild.button, href=subchild.anchor, className="header-navigation-dropdown-button"),
                            new_tab_button(href=subchild.anchor, className="header-navigation-dropdown-button-tab")
                        ], className="header-navigation-dropdown-group"))
                    navigation_group.append(dbc.DropdownMenu(dropdown_group, direction="down", className="header-navigation-dropdown"))
                navigation_items.append(dbc.ButtonGroup(navigation_group, className="header-navigation-group"))
            page._navigation_ = dbc.Navbar(navigation_items, className="header-navigation-bar")

    def _init_header_(self) -> Component:
        return html.Div([
            html.Div([
                html.Div([html.Img(src=self.app.get_asset_url("logo.png"), className="header-image")], className="header-logo"),
                html.Div([html.H1(self.name, className="header-title"), html.H4(self.team, className="header-team")], className="header-title-team"),
                html.Div([self.description], id=self._DESCRIPTION_ID_, className="header-description")
            ], className="header-information-block"),
            html.Div([
                html.Div(None, id=self._NAVIGATION_ID_, className="header-navigation-block"),
                *ButtonContainerAPI(background="primary", border="white", elements=[
                    ButtonAPI(id=self._BACKWARD_BUTTON_ID_, stylename="bi bi-arrow-left", trigger=self._BACKWARD_TRIGGER_ID_),
                    ButtonAPI(id=self._REFRESH_BUTTON_ID_, stylename="bi bi-arrow-repeat", trigger=self._REFRESH_TRIGGER_ID_),
                    ButtonAPI(id=self._FORWARD_BUTTON_ID_, stylename="bi bi-arrow-right", trigger=self._FORWARD_TRIGGER_ID_)
                ], stylename="header-location-block").build()
            ], className="header-control-block")
        ], className="header")

    def _init_content_(self) -> Component:
        return html.Div(children=[
                dbc.Collapse(children=[html.Div(children=[
                    self.DEVELOPMENT_LAYOUT
                ], id=self._SIDEBAR_ID_, className="sidebar-content")
                ], id=self._SIDEBAR_COLLAPSE_ID_, is_open=False, className="sidebar-collapse"),
                html.Div(children=[
                    self.LOADING_LAYOUT
                ], id=self._CONTENT_ID_, className="page-content"),
        ], className="content")

    def _init_footer_(self) -> Component:
        return html.Div([
            html.Div([
                *ButtonAPI(
                    id=self._SIDEBAR_BUTTON_ID_,
                    label=[IconAPI(icon="bi bi-layout-sidebar-inset")],
                    background="primary", border="white"
                ).build(),
                *ButtonAPI(
                    id=self._CONTACTS_BUTTON_ID_,
                    label=[
                        IconAPI(icon="bi bi-caret-down-fill", id=self._CONTACTS_ARROW_ID_),
                        TextAPI(text="  Contacts  "),
                        IconAPI(icon="bi bi-question-circle")
                    ], background="primary", border="white"
                ).build(),
            ], className="footer-left"),
            html.Div([
                *ButtonAPI(
                    id=self._CLEAN_CACHE_BUTTON_ID_,
                    label=[IconAPI(icon="bi bi-trash"), TextAPI(text="  Clean Cache  ")],
                    background="primary", border="white"
                ).build(),
                *ButtonAPI(
                    id=self._CLEAN_DATA_BUTTON_ID_,
                    label=[IconAPI(icon="bi bi-database-x"), TextAPI(text="  Clean Data  ")],
                    background="primary", border="white"
                ).build(),
                *ButtonAPI(
                    id=self._TERMINAL_BUTTON_ID_,
                    label=[IconAPI(icon="bi bi-terminal"), TextAPI(text="  Terminal  "), IconAPI(icon="bi bi-caret-down-fill", id=self._TERMINAL_ARROW_ID_)],
                    background="primary", border="white"
                ).build(),
            ], className="footer-right"),
            dbc.Collapse(dbc.Card(dbc.CardBody([
                html.Div([html.B("Team: "), html.Span(self.team)]),
                html.Div([html.B("Contact: "), html.A(self.contact, href=f"mailto:{self.contact}")])
            ]), className="footer-panel footer-panel-left"), id=self._CONTACTS_COLLAPSE_ID_, is_open=False),
            dbc.Collapse(dbc.Card(dbc.CardBody([
                html.Pre([], id=self._TERMINAL_ID_)
            ]), className="footer-panel footer-panel-right", color="dark", inverse=True), id=self._TERMINAL_COLLAPSE_ID_, is_open=False)
        ], className="footer")

    def _init_hidden_(self) -> Component:
        return html.Div([
            html.Div(id=self.CALLBACK_SINK_ID),
            dcc.Interval(id=self.INTERVAL_ID, interval=1000, n_intervals=0, disabled=False),
            dcc.Store(id=self._LOCATION_STORAGE_ID_, storage_type="session", data=LocationAPI().dict()),
            dcc.Store(id=self.NAVIGATION_STORAGE_ID, storage_type="session", data=NavigationAPI().dict()),
            dcc.Store(id=self.MEMORY_STORAGE_ID, storage_type="memory", data=dict()),
            dcc.Store(id=self.SESSION_STORAGE_ID, storage_type="session", data=dict()),
            dcc.Store(id=self.LOCAL_STORAGE_ID, storage_type="local", data=dict()),
            dcc.Location(id=self._LOCATION_ID_, refresh=False)
        ], className="hidden")

    def _init_layout_(self) -> None:
        header = self._init_header_()
        self._log_.debug(lambda: "Loaded Header Layout")
        content = self._init_content_()
        self._log_.debug(lambda: "Loaded Content Layout")
        footer = self._init_footer_()
        self._log_.debug(lambda: "Loaded Footer Layout")
        hidden = self._init_hidden_()
        self._log_.debug(lambda: "Loaded Hidden Layout")
        self.app.layout = html.Div(children=[header, content, footer, hidden], className="app")
        self._log_.debug(lambda: "Loaded App Layout")

    def _init_callbacks_(self) -> None:
        for context in [self] + list(self._pages_.values()):
            for cls in reversed(getmro(context)):
                if cls is object:
                    continue
                for name, func in cls.__dict__.items():
                    if not iscallable(func):
                        continue
                    if not getattr(func, "_callback_", False):
                        continue
                    bound = getattr(context, name)
                    callback_js: list = getattr(func, "_callback_js_")
                    callback_args: list = getattr(func, "_callback_args_")
                    callback_kwargs: dict = getattr(func, "_callback_kwargs_")
                    callback_args = [arg.build(context=context) if isinstance(arg, Trigger) else arg for arg in callback_args]
                    callback_kwargs.setdefault("prevent_initial_call", True)
                    if callback_js:
                        self.app.clientside_callback(bound(), *callback_args, **callback_kwargs)
                        self._log_.info(lambda: f"Loaded Client-Side Callback: {name}")
                    else:
                        self.app.callback(*callback_args, **callback_kwargs)(bound)
                        self._log_.info(lambda: f"Loaded Server-Side Callback: {name}")

    @serverside_callback(
        Output("_LOCATION_ID_", "pathname"),
        Output("_DESCRIPTION_ID_", "children"),
        Output("_NAVIGATION_ID_", "children"),
        Output("_SIDEBAR_ID_", "children"),
        Output("_CONTENT_ID_", "children"),
        Output("_LOCATION_STORAGE_ID_", "data"),
        Input("_LOCATION_ID_", "pathname"),
        State("_DESCRIPTION_ID_", "children"),
        State("_NAVIGATION_ID_", "children"),
        State("_SIDEBAR_ID_", "children"),
        State("_CONTENT_ID_", "children"),
        State("_LOCATION_STORAGE_ID_", "data"),
        prevent_initial_call=False
    )
    def _update_location_callback_(self, path: str, description: Component, navigation: Component, sidebar: Component, content: Component, location: dict):
        if path is None: raise PreventUpdate
        self._log_.debug(lambda: f"Update Location Callback: Received Path = {path}")
        anchor = self.anchorize(path=path, relative=False)
        self._log_.debug(lambda: f"Update Location Callback: Parsed Anchor = {anchor}")
        endpoint = self.endpointize(path=path, relative=False)
        self._log_.debug(lambda: f"Update Location Callback: Parsed Endpoint = {endpoint}")
        location = LocationAPI(**location or {})
        if location.current() == anchor:
            self._log_.debug(lambda: "Update Location Callback: Current Page Detected")
        elif location.backward(step=False) == anchor:
            self._log_.debug(lambda: "Update Location Callback: Backward Page Detected")
            location.backward(step=True)
        elif location.forward(step=False) == anchor:
            self._log_.debug(lambda: "Update Location Callback: Forward Page Detected")
            location.forward(step=True)
        else:
            location.register(path=anchor)
            self._log_.debug(lambda: "Update Location Callback: Registered Page")
        if path == anchor:
            anchor = dash.no_update
        else:
            self._log_.debug(lambda: f"Update Location Callback: Updating Anchor")
        if (page := self.locate(endpoint=endpoint)) is not None:
            self._log_.debug(lambda: f"Update Location Callback: Page Found")
            if description == page.description:
                description = dash.no_update
            elif self.description or not page.description:
                description = dash.no_update
            else:
                self._log_.debug(lambda: f"Update Location Callback: Updating Description")
                description = page.description
            if navigation is page._navigation_:
                navigation = dash.no_update
            elif not page._navigation_:
                navigation = dash.no_update
            else:
                self._log_.debug(lambda: f"Update Location Callback: Updating Navigation")
                navigation = page._navigation_
            if sidebar is page._sidebar_:
                sidebar = dash.no_update
            else:
                self._log_.debug(lambda: f"Update Location Callback: Updating Sidebar")
                sidebar = page._sidebar_
            if content is page._content_:
                content = dash.no_update
            else:
                self._log_.debug(lambda: f"Update Location Callback: Updating Content")
                content = page._content_
        else:
            self._log_.debug(lambda: f"Update Location Callback: Page Not Found")
            description = dash.no_update
            navigation = dash.no_update
            sidebar = self.NOT_FOUND_LAYOUT
            content = self.NOT_FOUND_LAYOUT
        if all([update is dash.no_update for update in [anchor, description, navigation, sidebar, content]]):
            self._log_.debug(lambda: f"Update Location Callback: No Updates Required")
            raise PreventUpdate
        return anchor, description, navigation, sidebar, content, location.dict()

    @clientside_callback(
        Output("CALLBACK_SINK_ID", "children", allow_duplicate=True),
        Input("NAVIGATION_STORAGE_ID", "data")
    )
    def _update_navigation_callback_(self):
        return """
        function(nav) {
            if (!nav || !nav.href || nav.index == null) {
                return window.dash_clientside.no_update;
            }
            const last = (window.__lastNavIndex__ ?? -1);
            if (nav.index <= last) {
                return window.dash_clientside.no_update;
            }
            window.__lastNavIndex__ = nav.index;
            const href = nav.href;
            if (nav.external) {
                window.open(href, "_blank", "noopener,noreferrer");
                return "";
            }
            window.history.pushState({}, "", href);
            window.dispatchEvent(new PopStateEvent("popstate"));
            return "";
        }
        """

    @serverside_callback(
        Output("_LOCATION_ID_", "pathname"),
        Output("_LOCATION_STORAGE_ID_", "data"),
        Input("_BACKWARD_BUTTON_ID_", "n_clicks"),
        State("_LOCATION_STORAGE_ID_", "data")
    )
    def _backward_location_callback_(self, clicks: int, location: dict):
        if clicks is None: raise PreventUpdate
        self._log_.debug(lambda: f"Backward Location Callback: Clicks = {clicks}")
        location = LocationAPI(**location or {})
        path = location.backward(step=True)
        if not path:
            self._log_.debug(lambda: "Backward Location Callback: No backward path available")
            raise PreventUpdate
        self._log_.debug(lambda: f"Backward Location Callback: Navigating to {path}")
        return path, location.dict()

    @clientside_callback(
        Output("CALLBACK_SINK_ID", "children"),
        Input("_REFRESH_BUTTON_ID_", "n_clicks"),
        Input("_REFRESH_TRIGGER_ID_", "data"),
    )
    def _refresh_location_callback_(self):
        return """
        function(clicks, trigger) {
            const clicked = (clicks != null && clicks > 0);
            const idx = (trigger && trigger.index != null) ? trigger.index : 0;
            const last = (window.__lastRefreshIndex__ ?? 0);
            const triggered = (idx > last);
            if (!clicked && !triggered) {
                return window.dash_clientside.no_update;
            }
            if (triggered) {
                window.__lastRefreshIndex__ = idx;
            }
            window.location.reload();
            return "";
        }
        """

    @serverside_callback(
        Output("_LOCATION_ID_", "pathname"),
        Output("_LOCATION_STORAGE_ID_", "data"),
        Input("_FORWARD_BUTTON_ID_", "n_clicks"),
        State("_LOCATION_STORAGE_ID_", "data")
    )
    def _forward_location_callback_(self, clicks: int, location: dict):
        if clicks is None: raise PreventUpdate
        self._log_.debug(lambda: f"Forward Location Callback: Clicks = {clicks}")
        location = LocationAPI(**location or {})
        path = location.forward(step=True)
        if not path:
            self._log_.debug(lambda: "Forward Location Callback: No forward path available")
            raise PreventUpdate
        self._log_.debug(lambda: f"Forward Location Callback: Navigating to {path}")
        return path, location.dict()

    def _collapse_button_callback_(self, name: str, was_open: bool, classname: str = None):
        is_open = not was_open
        self._log_.debug(lambda: f"{name} Callback: {'Expanding' if is_open else 'Collapsing'}")
        if not classname: return is_open
        elif is_open: classname = classname.replace("down", "up")
        else: classname = classname.replace("up", "down")
        return is_open, classname

    @serverside_callback(
        Output("_SIDEBAR_COLLAPSE_ID_", "is_open"),
        Input("_SIDEBAR_BUTTON_ID_", "n_clicks"),
        State("_SIDEBAR_COLLAPSE_ID_", "is_open")
    )
    def _sidebar_button_callback_(self, clicks: int, was_open: bool):
        if clicks is None: raise PreventUpdate
        return self._collapse_button_callback_(name="Sidebar", was_open=was_open)

    @serverside_callback(
        Output("_CONTACTS_COLLAPSE_ID_", "is_open"),
        Output("_CONTACTS_ARROW_ID_", "className"),
        Input("_CONTACTS_BUTTON_ID_", "n_clicks"),
        State("_CONTACTS_COLLAPSE_ID_", "is_open"),
        State("_CONTACTS_ARROW_ID_", "className")
    )
    def _contacts_button_callback_(self, clicks: int, was_open: bool, classname: str):
        if clicks is None: raise PreventUpdate
        return self._collapse_button_callback_(name="Contacts", was_open=was_open, classname=classname)

    @serverside_callback(
        Output("MEMORY_STORAGE_ID", "data"),
        Output("SESSION_STORAGE_ID", "data"),
        Output("_REFRESH_TRIGGER_ID_", "data"),
        Input("_CLEAN_CACHE_BUTTON_ID_", "n_clicks"),
        State("_REFRESH_TRIGGER_ID_", "data")
    )
    def _clean_cache_callback_(self, clicks: int, trigger: dict):
        if clicks is None: raise PreventUpdate
        button = TriggerAPI(**trigger or {})
        self._log_.debug(lambda: "Clean Cache Callback: Cleaning Cache")
        memory = {}
        session = {}
        self._log_.debug(lambda: "Clean Cache Callback: Cleaned Data")
        button.trigger()
        self._log_.debug(lambda: "Clean Cache Callback: Refreshing Page")
        return memory, session, button.dict()

    @serverside_callback(
        Output("MEMORY_STORAGE_ID", "data"),
        Output("SESSION_STORAGE_ID", "data"),
        Output("LOCAL_STORAGE_ID", "data"),
        Output("_REFRESH_TRIGGER_ID_", "data"),
        Input("_CLEAN_DATA_BUTTON_ID_", "n_clicks"),
        State("_REFRESH_TRIGGER_ID_", "data")
    )
    def _clean_data_callback_(self, clicks: int, trigger: dict):
        if clicks is None: raise PreventUpdate
        button = TriggerAPI(**trigger or {})
        self._log_.debug(lambda: "Clean Data Callback: Cleaning Data")
        memory = {}
        session = {}
        local = {}
        self._log_.debug(lambda: "Clean Data Callback: Cleaned Data")
        button.trigger()
        self._log_.debug(lambda: "Clean Data Callback: Refreshing Page")
        return memory, session, local, button.dict()

    @serverside_callback(
        Output("_TERMINAL_COLLAPSE_ID_", "is_open"),
        Output("_TERMINAL_ARROW_ID_", "className"),
        Input("_TERMINAL_BUTTON_ID_", "n_clicks"),
        State("_TERMINAL_COLLAPSE_ID_", "is_open"),
        State("_TERMINAL_ARROW_ID_", "className")
    )
    def _terminal_button_callback_(self, clicks: int, was_open: bool, classname: str):
        if clicks is None: raise PreventUpdate
        return self._collapse_button_callback_(name="Terminal", was_open=was_open, classname=classname)

    @serverside_callback(
        Output("_TERMINAL_ID_", "children"),
        Input("INTERVAL_ID", "n_intervals"),
        State("_TERMINAL_ID_", "children")
    )
    def _terminal_stream_callback_(self, _, terminal: list[Component]):
        logs = self._log_.web.stream()
        if not logs: raise PreventUpdate
        terminal = terminal or []
        terminal.extend(logs)
        return terminal[-self.terminal:]

    def ids(self) -> None:
        pass

    def pages(self) -> None:
        pass

    def run(self):
        return self.app.run(
            host=self.host,
            port=self.port,
            proxy=self.proxy,
            debug=self.debug,
            jupyter_mode="external",
            jupyter_server_url=self.domain_url
        )

    def mount(self):
        app = FastAPI()
        app.mount("/", WSGIMiddleware(self.app.server))
        return app
