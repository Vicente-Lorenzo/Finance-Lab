import base64
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash._callback_context import CallbackContext
from pathlib import PurePosixPath

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from Library.App import *
from Library.Logging import *
from Library.Utility.HTML import *
from Library.Utility.Path import *
from Library.Utility.Typing import *
from Library.Utility.Runtime import *
from Library.Utility.IO import *

class AppAPI:

    GLOBAL_LOCATION_ID: dict
    GLOBAL_LOCATION_STORAGE_ID: dict
    GLOBAL_DESCRIPTION_ID: dict
    GLOBAL_NAVIGATION_ID: dict
    GLOBAL_CONTENT_ID: dict
    GLOBAL_CONTENT_LOADING_ID: dict
    GLOBAL_SIDEBAR_ID: dict
    GLOBAL_SIDEBAR_BUTTON_ID: dict
    GLOBAL_SIDEBAR_LOADING_ID: dict
    GLOBAL_SIDEBAR_COLLAPSE_ID: dict

    GLOBAL_BACKWARD_BUTTON_ID: dict
    GLOBAL_BACKWARD_TRIGGER_ID: dict
    GLOBAL_REFRESH_BUTTON_ID: dict
    GLOBAL_REFRESH_TRIGGER_ID: dict
    GLOBAL_FORWARD_BUTTON_ID: dict
    GLOBAL_FORWARD_TRIGGER_ID: dict

    GLOBAL_CONTACTS_ARROW_ID: dict
    GLOBAL_CONTACTS_BUTTON_ID: dict
    GLOBAL_CONTACTS_COLLAPSE_ID: dict
    GLOBAL_CONTACTS_ID: dict

    GLOBAL_IMPORT_ID: dict
    GLOBAL_IMPORT_UPLOAD_ID: dict
    GLOBAL_EXPORT_ID: dict
    GLOBAL_EXPORT_DOWNLOAD_ID: dict

    GLOBAL_TERMINAL_ID: dict
    GLOBAL_TERMINAL_ARROW_ID: dict
    GLOBAL_TERMINAL_BUTTON_ID: dict
    GLOBAL_TERMINAL_COLLAPSE_ID: dict
    GLOBAL_TERMINAL_INTERVAL_ID: dict

    GLOBAL_LOADING_TRIGGER_ID: dict
    GLOBAL_ROUTING_STORAGE_ID: dict
    GLOBAL_RELOADING_TRIGGER_ID: dict
    GLOBAL_UNLOADING_TRIGGER_ID: dict

    GLOBAL_MEMORY_STORAGE_ID: dict
    GLOBAL_CLEAN_MEMORY_BUTTON_ID: dict
    GLOBAL_CLEAN_MEMORY_TRIGGER_ID: dict
    GLOBAL_SESSION_STORAGE_ID: dict
    GLOBAL_CLEAN_SESSION_BUTTON_ID: dict
    GLOBAL_CLEAN_SESSION_TRIGGER_ID: dict
    GLOBAL_LOCAL_STORAGE_ID: dict
    GLOBAL_CLEAN_LOCAL_BUTTON_ID: dict
    GLOBAL_CLEAN_LOCAL_TRIGGER_ID: dict

    GLOBAL_NOT_FOUND_LAYOUT: Component
    GLOBAL_LOADING_LAYOUT: Component
    GLOBAL_MAINTENANCE_LAYOUT: Component
    GLOBAL_DEVELOPMENT_LAYOUT: Component
    GLOBAL_NOT_INDEXED_LAYOUT: Component

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

        self._log_ = HandlerLoggingAPI(AppAPI.__name__)

        self._ids_: set = set()
        self._pages_: dict[str, PageAPI] = {}
        self._loaders_: list[str] = []
        self._reloaders_: list[str] = []
        self._unloaders_: list[str] = []

        self._name_: str = name
        self._log_.debug(lambda: f"Defined Name = {self._name_}")
        self._title_: str = title
        self._log_.debug(lambda: f"Defined Title = {self._title_}")
        self._team_: str = team
        self._log_.debug(lambda: f"Defined Team = {self._team_}")
        self._description_: str = description
        self._log_.debug(lambda: f"Defined Description = {self._description_}")
        self._contact_: str = contact
        self._log_.debug(lambda: f"Defined Contact = {self._contact_}")
        self._update_: str = update
        self._log_.debug(lambda: f"Defined Update = {self._update_}")

        host: str = host or "localhost"
        self._host_: str = inspect_file_path(host, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Host = {self._host_}")
        self._port_: int = port or find_host_port(host=self._host_, port_min=8050)
        self._log_.debug(lambda: f"Defined Port = {self._port_}")

        protocol: str = protocol or "http"
        self._protocol_: str = inspect_file_path(protocol, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Protocol = {self._protocol_}")

        host_address: str = f"{self._host_}:{self._port_}"
        self._host_address_: str = inspect_file_path(host_address, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Host Address = {self._host_address_}")
        self._host_url_: str = f"{self._protocol_}://{self._host_address_}"
        self._log_.debug(lambda: f"Defined Host URL = {self._host_url_}")

        domain_address: str = domain or self._host_address_
        self._domain_address_: str = inspect_file_path(domain_address, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Domain Address = {self._domain_address_}")
        self._domain_url_: str = f"{self._protocol_}://{self._domain_address_}"
        self._log_.debug(lambda: f"Defined Domain URL = {self._domain_url_}")

        self._proxy_: str = proxy or f"{self._host_url_}::{self._domain_url_}"
        self._log_.debug(lambda: f"Defined Proxy = {self._proxy_}")

        anchor: str = anchor or "/"
        self._anchor_: PurePath = inspect_file(anchor, header=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Anchor = {self._anchor_}")
        self._endpoint_: str = inspect_file_path(anchor, header=True, footer=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Defined Endpoint = {self._endpoint_}")

        self._debug_: bool = debug
        self._log_.debug(lambda: f"Defined Debug = {self._debug_}")
        self._terminal_: int = terminal
        self._log_.debug(lambda: f"Defined Terminal = {self._terminal_}")

        self._library_: Path = traceback_current_module(resolve=True)
        self._log_.debug(lambda: f"Defined Library = {self._library_}")
        self._library_assets_: Path = self._library_ / "Assets"
        self._log_.debug(lambda: f"Defined Library Assets = {self._library_assets_}")
        self._application_: Path = traceback_calling_module(resolve=True)
        self._log_.debug(lambda: f"Defined Application = {self._application_}")
        self._application_assets_: Path = self._application_ / "Assets"
        self._log_.debug(lambda: f"Defined Application Assets = {self._application_assets_}")
        self._application_assets_url_: str = "Assets"
        self._log_.debug(lambda: f"Defined Application Assets URL = {self._application_assets_url_}")

        self._init_assets_()
        self._log_.debug(lambda: "Initialized Assets")

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

        self.ctx: CallbackContext = dash.callback_context
        self._log_.info(lambda: "Initialized Context")

    def _init_assets_(self) -> None:
        writable, created, updated, removed, conflicts, _ = mirror(
            src_root=self._library_assets_,
            dst_root=self._application_assets_,
            subdirs=(".", "Styles", "Images", "Callbacks", "Data"),
            manifest_name="manifest.json"
        )
        if writable:
            self._log_.debug(lambda: "Init Assets: Mirrored Assets")
        if not writable:
            self._log_.debug(lambda: "Init Assets: Mirroring Aborted (Read-Only)")
        if conflicts:
            self._log_.warning(lambda: f"Init Assets: {conflicts} Conflicts Detected")

    def _init_ids_(self) -> None:
        self.GLOBAL_LOCATION_ID: dict = self.register(type="location", name="location")
        self.GLOBAL_LOCATION_STORAGE_ID: dict = self.register(type="storage", name="location")
        self.GLOBAL_DESCRIPTION_ID: dict = self.register(type="div", name="description")
        self.GLOBAL_NAVIGATION_ID: dict = self.register(type="navigator", name="navigation")
        self.GLOBAL_CONTENT_ID: dict = self.register(type="div", name="content")
        self.GLOBAL_CONTENT_LOADING_ID: dict = self.register(type="loading", name="content")
        self.GLOBAL_SIDEBAR_ID: dict = self.register(type="div", name="sidebar")
        self.GLOBAL_SIDEBAR_BUTTON_ID: dict = self.register(type="button", name="sidebar")
        self.GLOBAL_SIDEBAR_LOADING_ID: dict = self.register(type="loading", name="sidebar")
        self.GLOBAL_SIDEBAR_COLLAPSE_ID: dict = self.register(type="collapse", name="sidebar")

        self.GLOBAL_BACKWARD_BUTTON_ID: dict = self.register(type="button", name="backward")
        self.GLOBAL_BACKWARD_TRIGGER_ID = self.register(type="trigger", name="backward")
        self.GLOBAL_REFRESH_BUTTON_ID: dict = self.register(type="button", name="refresh")
        self.GLOBAL_REFRESH_TRIGGER_ID = self.register(type="trigger", name="refresh")
        self.GLOBAL_FORWARD_BUTTON_ID: dict = self.register(type="button", name="forward")
        self.GLOBAL_FORWARD_TRIGGER_ID = self.register(type="trigger", name="forward")

        self.GLOBAL_CONTACTS_ARROW_ID: dict = self.register(type="icon", name="contacts")
        self.GLOBAL_CONTACTS_BUTTON_ID: dict = self.register(type="button", name="contacts")
        self.GLOBAL_CONTACTS_COLLAPSE_ID: dict = self.register(type="collapse", name="contacts")
        self.GLOBAL_CONTACTS_ID: dict = self.register(type="card", name="contacts")

        self.GLOBAL_IMPORT_ID: dict = self.register(type="button", name="import")
        self.GLOBAL_IMPORT_UPLOAD_ID: dict = self.register(type="upload", name="import")
        self.GLOBAL_EXPORT_ID: dict = self.register(type="button", name="export")
        self.GLOBAL_EXPORT_DOWNLOAD_ID: dict = self.register(type="download", name="export")

        self.GLOBAL_TERMINAL_ID: dict = self.register(type="card", name="terminal")
        self.GLOBAL_TERMINAL_ARROW_ID: dict = self.register(type="icon", name="terminal")
        self.GLOBAL_TERMINAL_BUTTON_ID: dict = self.register(type="button", name="terminal")
        self.GLOBAL_TERMINAL_COLLAPSE_ID: dict = self.register(type="collapse", name="terminal")
        self.GLOBAL_TERMINAL_INTERVAL_ID: dict = self.register(type="interval", name="terminal")

        self.GLOBAL_LOADING_TRIGGER_ID: dict = self.register(type="trigger", name="loading")
        self.GLOBAL_ROUTING_STORAGE_ID: dict = self.register(type="storage", name="routing")
        self.GLOBAL_RELOADING_TRIGGER_ID: dict = self.register(type="trigger", name="reloading")
        self.GLOBAL_UNLOADING_TRIGGER_ID: dict = self.register(type="trigger", name="unloading")

        self.GLOBAL_MEMORY_STORAGE_ID: dict = self.register(type="storage", name="memory")
        self.GLOBAL_CLEAN_MEMORY_BUTTON_ID: dict = self.register(type="button", name="memory")
        self.GLOBAL_CLEAN_MEMORY_TRIGGER_ID: dict = self.register(type="trigger", name="memory")
        self.GLOBAL_SESSION_STORAGE_ID: dict = self.register(type="storage", name="session")
        self.GLOBAL_CLEAN_SESSION_BUTTON_ID: dict = self.register(type="button", name="session")
        self.GLOBAL_CLEAN_SESSION_TRIGGER_ID: dict = self.register(type="trigger", name="session")
        self.GLOBAL_LOCAL_STORAGE_ID: dict = self.register(type="storage", name="local")
        self.GLOBAL_CLEAN_LOCAL_BUTTON_ID: dict = self.register(type="button", name="local")
        self.GLOBAL_CLEAN_LOCAL_TRIGGER_ID: dict = self.register(type="trigger", name="local")

        self.ids()

    def _init_app_(self) -> None:
        self.app = dash.Dash(
            name=self._name_,
            title=self._title_,
            update_title=self._update_,
            routes_pathname_prefix=self._endpoint_,
            requests_pathname_prefix=self._endpoint_,
            assets_url_path=self._application_assets_url_,
            assets_folder=inspect_path(self._application_assets_),
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
            suppress_callback_exceptions=True,
            prevent_initial_callbacks=True
        )
        self._init_ids_()

    def _init_pages_(self) -> None:
        self.GLOBAL_NOT_FOUND_LAYOUT = DefaultLayoutAPI(
            image=self.asset("Images/404.png"),
            title="Resource Not Found",
            description="Unable to find the resource you are looking for.",
            details="Please check the url path."
        ).build()
        self.GLOBAL_LOADING_LAYOUT = DefaultLayoutAPI(
            image=self.asset("Images/loading.gif"),
            title="Loading...",
            description="This resource is loading its content.",
            details="Please wait a moment."
        ).build()
        self.GLOBAL_MAINTENANCE_LAYOUT = DefaultLayoutAPI(
            image=self.asset("Images/maintenance.png"),
            title="Resource Under Maintenance",
            description="This resource is temporarily down for maintenance.",
            details="Please try again later."
        ).build()
        self.GLOBAL_DEVELOPMENT_LAYOUT = DefaultLayoutAPI(
            image=self.asset("Images/development.png"),
            title="Resource Under Development",
            description="This resource is currently under development.",
            details="Please try again later."
        ).build()
        self.GLOBAL_NOT_INDEXED_LAYOUT = DefaultLayoutAPI(
            image=self.asset("Images/indexed.png"),
            title="Resource Not Indexed",
            description="This resource is not indexed at any page.",
            details="Please try again later."
        ).build()
        self.pages()

    def _init_navigation_(self) -> None:
        for endpoint, page in self._pages_.items():
            if not page.parent and not page.children:
                page._navigation_ = []
                self._log_.debug(lambda: f"Init Navigation: Loaded Page = {endpoint} with No Navigation")
                continue
            if page.parent and not page.children:
                page._navigation_ = page.parent._navigation_
                self._log_.debug(lambda: f"Init Navigation: Loaded Page = {endpoint} with Parent Navigation")
                continue
            currents = []
            for b in page.backwards():
                backward = PaginatorAPI(
                    href=b.endpoint,
                    label=[IconAPI(icon="bi bi-arrow-bar-left"), TextAPI(text=f"  {b.button}")],
                    background="white",
                    outline_color="black",
                    outline_style="solid",
                    outline_width="1px",
                )
                currents.append(NavigatorAPI(element=backward, typename="header-navigation"))
            for c in page.currents():
                forwards = []
                for f in page.forwards(c):
                    forward = PaginatorAPI(
                        href=f.endpoint,
                        label=[TextAPI(text=f.button)],
                        background="white"
                    )
                    forwards.append(DropdownAPI(element=forward))
                dropdown = DropdownContainerAPI(
                    elements=forwards,
                    background="white",
                    align_end=True
                ) if forwards else None
                current = PaginatorAPI(
                    href=c.endpoint,
                    label=[TextAPI(text=c.button)],
                    dropdown=dropdown,
                    background="white",
                    outline_color="black",
                    outline_style="solid",
                    outline_width="1px",
                )
                currents.append(NavigatorAPI(element=current, typename="header-navigation"))
            page._navigation_ = NavigatorContainerAPI(elements=currents).build()

    def _init_header_(self) -> Component:
        return html.Div(children=[
            html.Div(children=[
                html.Div(children=[html.Img(src=self.asset("Images/logo.png"), className="header-image")], className="header-logo"),
                html.Div(children=[html.H1(self._name_, className="header-title"), html.H4(self._team_, className="header-team")], className="header-title-team"),
                html.Div(children=[self._description_], id=self.GLOBAL_DESCRIPTION_ID, className="header-description")
            ], className="header-information-block"),
            html.Div(children=[
                html.Div(children=[
                ], className="header-navigation-block", id=self.GLOBAL_NAVIGATION_ID),
                html.Div(children=[
                    *ButtonContainerAPI(elements=[
                        ButtonAPI(id=self.GLOBAL_BACKWARD_BUTTON_ID, label=[IconAPI(icon="bi bi-arrow-left")], trigger=self.GLOBAL_BACKWARD_TRIGGER_ID),
                        ButtonAPI(id=self.GLOBAL_REFRESH_BUTTON_ID, label=[IconAPI(icon="bi bi-arrow-repeat")], trigger=self.GLOBAL_REFRESH_TRIGGER_ID),
                        ButtonAPI(id=self.GLOBAL_FORWARD_BUTTON_ID, label=[IconAPI(icon="bi bi-arrow-right")], trigger=self.GLOBAL_FORWARD_TRIGGER_ID)
                    ], background="primary").build()
                ], className="header-location-block")
            ], className="header-control-block")
        ], className="header")

    def _init_content_(self) -> Component:
        return html.Div(children=[
                dbc.Collapse(children=[html.Div(children=[
                    self.GLOBAL_LOADING_LAYOUT
                ], id=self.GLOBAL_SIDEBAR_ID, className="sidebar-content")
                ], id=self.GLOBAL_SIDEBAR_COLLAPSE_ID, is_open=False, className="sidebar-collapse"),
                html.Div(children=[
                    self.GLOBAL_LOADING_LAYOUT
                ], id=self.GLOBAL_CONTENT_ID, className="page-content"),
        ], className="content")

    def _init_footer_(self) -> Component:
        return html.Div(children=[
            html.Div(children=[
                *ButtonAPI(id=self.GLOBAL_SIDEBAR_BUTTON_ID, background="primary",
                           label=[IconAPI(icon="bi bi-layout-sidebar-inset")]
                           ).build(),
                *ButtonAPI(id=self.GLOBAL_CONTACTS_BUTTON_ID, background="primary",
                           label=[IconAPI(icon="bi bi-caret-down-fill", id=self.GLOBAL_CONTACTS_ARROW_ID), TextAPI(text="  Contacts  "), IconAPI(icon="bi bi-question-circle")]
                           ).build(),
                *ButtonAPI(id=self.GLOBAL_IMPORT_ID, upload=self.GLOBAL_IMPORT_UPLOAD_ID, background="warning",
                           label=[TextAPI(text="Import Snapshot  "), IconAPI(icon="bi bi-upload")]
                           ).build(),
                *ButtonAPI(id=self.GLOBAL_EXPORT_ID, download=self.GLOBAL_EXPORT_DOWNLOAD_ID, background="warning",
                           label=[TextAPI(text="Export Snapshot  "), IconAPI(icon="bi bi-download")]
                           ).build()
            ], className="footer-left"),
            html.Div(children=[
                *ButtonAPI(id=self.GLOBAL_CLEAN_MEMORY_BUTTON_ID, background="danger",
                           label=[IconAPI(icon="bi bi-trash"), TextAPI(text="  Clean Memory  ")],
                           trigger=self.GLOBAL_CLEAN_MEMORY_TRIGGER_ID
                           ).build(),
                *ButtonAPI(id=self.GLOBAL_CLEAN_SESSION_BUTTON_ID, background="danger",
                           label=[IconAPI(icon="bi bi-database-x"), TextAPI(text="  Clean Session  ")],
                           trigger=self.GLOBAL_CLEAN_SESSION_TRIGGER_ID
                           ).build(),
                *ButtonAPI(id=self.GLOBAL_CLEAN_LOCAL_BUTTON_ID, background="danger",
                           label=[IconAPI(icon="bi bi-x-octagon"), TextAPI(text="  Clean Local  ")],
                           trigger=self.GLOBAL_CLEAN_LOCAL_TRIGGER_ID
                           ).build(),
                *ButtonAPI(id=self.GLOBAL_TERMINAL_BUTTON_ID, background="primary",
                           label=[IconAPI(icon="bi bi-terminal"), TextAPI(text="  Terminal  "), IconAPI(icon="bi bi-caret-down-fill", id=self.GLOBAL_TERMINAL_ARROW_ID)]
                           ).build()
            ], className="footer-right"),
            dbc.Collapse(dbc.Card(dbc.CardBody([
                html.Div(children=[html.B("Team: "), html.Span(self._team_)]),
                html.Div(children=[html.B("Contact: "), html.A(self._contact_, href=f"mailto:{self._contact_}")])
            ]), className="footer-panel footer-panel-left"), id=self.GLOBAL_CONTACTS_COLLAPSE_ID, is_open=False),
            dbc.Collapse(dbc.Card(dbc.CardBody([
                html.Pre([], id=self.GLOBAL_TERMINAL_ID)
            ]), className="footer-panel footer-panel-right", color="dark", inverse=True), id=self.GLOBAL_TERMINAL_COLLAPSE_ID, is_open=False)
        ], className="footer")

    def _init_hidden_(self) -> Component:
        return html.Div(children=[
            dcc.Location(id=self.GLOBAL_LOCATION_ID, refresh=False),
            dcc.Store(id=self.GLOBAL_LOCATION_STORAGE_ID, storage_type="session", data=dict()),
            dcc.Store(id=self.GLOBAL_LOADING_TRIGGER_ID, storage_type="memory", data=dict()),
            dcc.Store(id=self.GLOBAL_ROUTING_STORAGE_ID, storage_type="memory", data=dict()),
            dcc.Store(id=self.GLOBAL_RELOADING_TRIGGER_ID, storage_type="memory", data=dict()),
            dcc.Store(id=self.GLOBAL_UNLOADING_TRIGGER_ID, storage_type="memory", data=dict()),
            dcc.Interval(id=self.GLOBAL_TERMINAL_INTERVAL_ID, interval=1000, n_intervals=0, disabled=False),
            dcc.Store(id=self.GLOBAL_MEMORY_STORAGE_ID, storage_type="memory", data=dict()),
            dcc.Store(id=self.GLOBAL_SESSION_STORAGE_ID, storage_type="session", data=dict()),
            dcc.Store(id=self.GLOBAL_LOCAL_STORAGE_ID, storage_type="local", data=dict())
        ], className="hidden")

    def _init_layout_(self) -> None:
        header = self._init_header_()
        self._log_.debug(lambda: "Init Layout: Loaded Header Layout")
        content = self._init_content_()
        self._log_.debug(lambda: "Init Layout: Loaded Content Layout")
        footer = self._init_footer_()
        self._log_.debug(lambda: "Init Layout: Loaded Footer Layout")
        hidden = self._init_hidden_()
        self._log_.debug(lambda: "Init Layout: Loaded Hidden Layout")
        layout = html.Div(children=[header, content, footer, hidden], className="app")
        self.app.layout = layout
        self._log_.debug(lambda: "Init Layout: Loaded App Layout")

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
                    client: bool = func._callback_js_
                    args: list = func._callback_args_
                    kwargs: dict = func._callback_kwargs_
                    loading: bool = func._callback_loading_
                    reloading: bool = func._callback_reloading_
                    unloading: bool = func._callback_unloading_
                    args = [arg.build(context=context) if isinstance(arg, Trigger) else arg for arg in args]
                    if client:
                        javascript = bound()
                        if loading:
                            trigger = context.loader(name=name)
                            handler_args = [dash.Input(trigger, "data")]
                            javascript, args = override_clientside_callback(
                                handler_func=None,
                                handler_args=handler_args,
                                original_js=javascript,
                                original_args=args
                            )
                        if reloading:
                            trigger = context.reloader(name=name)
                            handler_args = [dash.Input(trigger, "data")]
                            javascript, args = override_clientside_callback(
                                handler_func=None,
                                handler_args=handler_args,
                                original_js=javascript,
                                original_args=args
                            )
                        if unloading:
                            trigger = context.unloader(name=name)
                            handler_args = [dash.Input(trigger, "data")]
                            javascript, args = override_clientside_callback(
                                handler_func=None,
                                handler_args=handler_args,
                                original_js=javascript,
                                original_args=args
                            )
                        self.app.clientside_callback(javascript, *args, **kwargs)
                        self._log_.info(lambda: f"Init Callbacks: Loaded Client-Side Callback: {name}")
                    else:
                        if loading:
                            trigger = context.loader(name=name)
                            handler_args = [dash.Input(trigger, "data")]
                            bound, args = override_serverside_callback(
                                handler_func=None,
                                handler_args=handler_args,
                                original_func=bound,
                                original_args=args
                            )
                        if reloading:
                            trigger = context.reloader(name=name)
                            handler_args = [dash.Input(trigger, "data")]
                            bound, args = override_serverside_callback(
                                handler_func=None,
                                handler_args=handler_args,
                                original_func=bound,
                                original_args=args
                            )
                        if unloading:
                            trigger = context.unloader(name=name)
                            handler_args = [dash.Input(trigger, "data")]
                            bound, args = override_serverside_callback(
                                handler_func=None,
                                handler_args=handler_args,
                                original_func=bound,
                                original_args=args
                            )
                        self.app.callback(*args, **kwargs)(bound)
                        self._log_.info(lambda: f"Init Callbacks: Loaded Server-Side Callback: {name}")

    def asset(self, path: str) -> str:
        return self.app.get_asset_url(path)

    def identify(self, *, page: str = None, type: str, name: str, portable: str = "", **kwargs) -> dict:
        page = page or "global"
        return {"app": self.__class__.__name__, "page": page, "type": type, "name": name, "portable": portable, **kwargs}

    def register(self, *, page: str = "global", type: str, name: str, portable: str = "", **kwargs) -> dict:
        cid = self.identify(page=page, type=type, name=name, portable=portable, **kwargs)
        key = (cid["app"], cid["page"], cid["type"], cid["name"], cid["portable"])
        if key in self._ids_: raise RuntimeError(f"Duplicate Dash ID detected: {cid}")
        self._ids_.add(key)
        return cid

    def resolve(self, path: PurePath | str, relative: bool, footer: bool = None) -> str:
        path = inspect_file(path, header=False, builder=PurePosixPath)
        self._log_.debug(lambda: f"Resolve Path: Received = {path}")
        path = self._anchor_ / path if relative else path
        resolve = inspect_file_path(path, header=True, footer=footer, builder=PurePosixPath)
        self._log_.debug(lambda: f"Resolve Path: Resolved = {resolve}")
        return resolve

    def anchorize(self, path: PurePath | str, relative: bool = True) -> str:
        return self.resolve(path, relative=relative, footer=False)

    def endpointize(self, path: PurePath | str, relative: bool = True) -> str:
        return self.resolve(path, relative=relative, footer=True)

    def locate(self, endpoint: str) -> tuple[str, PageAPI | None]:
        page = self._pages_.get(endpoint, None)
        if page: self._log_.debug(lambda: f"Locate Page: Found = {endpoint}")
        else: self._log_.debug(lambda: f"Locate Page: Not Found = {endpoint}")
        return endpoint, page

    def redirect(self, endpoint: str) -> tuple[str, PageAPI | None]:
        endpoint, page = self.locate(endpoint=endpoint)
        while page and page.endpoint != page.redirect:
            self._log_.debug(lambda: f"Redirect Page: Redirect = {page.endpoint} -> {page.redirect}")
            endpoint, page = self.locate(endpoint=page.redirect)
        return endpoint, page

    def index(self, endpoint: str, page: PageAPI) -> None:
        self._pages_[endpoint] = page

    def link(self, page: PageAPI) -> None:
        relative_path = inspect_file(page.path, header=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Page Linking: Relative Path = {relative_path}")
        relative_anchor = self.anchorize(path=relative_path, relative=True)
        self._log_.debug(lambda: f"Page Linking: Relative Anchor = {relative_anchor}")
        relative_endpoint = self.endpointize(path=relative_path, relative=True)
        self._log_.debug(lambda: f"Page Linking: Relative Endpoint = {relative_endpoint}")
        intermediate_alias = inspect_file("/", builder=PurePosixPath)
        _, intermediate_parent = self.locate(endpoint=self.endpointize(path=intermediate_alias, relative=True))
        for part in relative_path.parts[1:-1]:
            intermediate_path = inspect_file(part, header=True, builder=PurePosixPath)
            intermediate_alias /= intermediate_path.name
            self._log_.debug(lambda: f"Page Linking: Intermediate Path = {intermediate_alias}")
            intermediate_anchor = self.anchorize(path=intermediate_alias, relative=True)
            self._log_.debug(lambda: f"Page Linking: Intermediate Anchor = {intermediate_anchor}")
            intermediate_endpoint = self.endpointize(path=intermediate_alias, relative=True)
            self._log_.debug(lambda: f"Page Linking: Intermediate Endpoint = {intermediate_endpoint}")
            _, intermediate_page = self.locate(endpoint=intermediate_endpoint)
            if not intermediate_page:
                intermediate_page = PageAPI(
                    app=self,
                    path=inspect_path(intermediate_alias),
                    description="Resource Not Indexed",
                    add_backward_parent=True,
                    add_backward_children=False,
                    add_current_parent=False,
                    add_current_children=False,
                    add_forward_parent=False,
                    add_forward_children=False
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
        _, existing = self.locate(endpoint=relative_endpoint)
        if existing:
            page.merge(existing)
            self._log_.debug(lambda: f"Page Linking: Merged Relative Page = {relative_endpoint}")
        else:
            self.index(endpoint=page.endpoint, page=page)
            self._log_.info(lambda: f"Page Linking: Linked {page}")
        page.attach(parent=intermediate_parent)
        page._init_()

    def loader(self, name: str) -> dict:
        self._loaders_.append(name)
        return self.GLOBAL_LOADING_TRIGGER_ID

    def reloader(self, name: str) -> dict:
        self._reloaders_.append(name)
        return self.GLOBAL_RELOADING_TRIGGER_ID

    def unloader(self, name: str) -> dict:
        self._unloaders_.append(name)
        return self.GLOBAL_UNLOADING_TRIGGER_ID

    @clientside_callback(
        Input("GLOBAL_ROUTING_STORAGE_ID", "data")
    )
    def _global_routing_location_callback_(self):
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
        }
        """

    @serverside_callback(
        Output("GLOBAL_LOCATION_ID", "pathname"),
        Output("GLOBAL_LOCATION_STORAGE_ID", "data"),
        Output("GLOBAL_DESCRIPTION_ID", "children"),
        Output("GLOBAL_NAVIGATION_ID", "children"),
        Output("GLOBAL_SIDEBAR_ID", "children"),
        Output("GLOBAL_CONTENT_ID", "children"),
        Output("GLOBAL_LOADING_TRIGGER_ID", "data"),
        Output("GLOBAL_RELOADING_TRIGGER_ID", "data"),
        Input("GLOBAL_LOCATION_ID", "pathname"),
        State("GLOBAL_LOCATION_STORAGE_ID", "data"),
        State("GLOBAL_LOADING_TRIGGER_ID", "data"),
        State("GLOBAL_RELOADING_TRIGGER_ID", "data"),
        enable_initial_call=False
    )
    def _global_update_location_callback_(self, path: str, location: dict, loading: dict, reloading: dict):
        self._log_.debug(lambda: f"Update Location Callback: Received Path = {path}")
        anchor = self.anchorize(path=path, relative=False)
        self._log_.debug(lambda: f"Update Location Callback: Parsed Anchor = {anchor}")
        endpoint = self.endpointize(path=path, relative=False)
        self._log_.debug(lambda: f"Update Location Callback: Parsed Endpoint = {endpoint}")
        location = LocationAPI(**location)
        loading = TriggerAPI(**loading)
        reloading = TriggerAPI(**reloading)
        if location.current() == endpoint:
            self._log_.debug(lambda: "Update Location Callback: Current Page Detected")
            loading = dash.no_update
            reloading = reloading.trigger().dict()
        elif location.backward(step=False) == endpoint:
            self._log_.debug(lambda: "Update Location Callback: Backward Page Detected")
            location.backward(step=True)
            loading = loading.trigger().dict()
            reloading = dash.no_update
        elif location.forward(step=False) == endpoint:
            self._log_.debug(lambda: "Update Location Callback: Forward Page Detected")
            location.forward(step=True)
            loading = loading.trigger().dict()
            reloading = dash.no_update
        else:
            self._log_.debug(lambda: "Update Location Callback: New Page Detected")
            location.register(path=endpoint)
            loading = loading.trigger().dict()
            reloading = dash.no_update
        redirect, page = self.redirect(endpoint=endpoint)
        anchor = self.anchorize(path=redirect, relative=False)
        self._log_.debug(lambda: f"Update Location Callback: Normalized Anchor")
        if page:
            description = dash.no_update if (self._description_ or not page.description) else page.description
            self._log_.debug(lambda: f"Update Location Callback: Updated Description")
            navigation = page._navigation_ if page._navigation_ else dash.no_update
            self._log_.debug(lambda: f"Update Location Callback: Updated Navigation")
            sidebar = page._sidebar_
            self._log_.debug(lambda: f"Update Location Callback: Updated Sidebar")
            content = page._content_
            self._log_.debug(lambda: f"Update Location Callback: Updated Content")
        else:
            description = dash.no_update
            self._log_.debug(lambda: f"Update Location Callback: Did not Update Description")
            navigation = dash.no_update
            self._log_.debug(lambda: f"Update Location Callback: Did not Update Navigation")
            sidebar = self.GLOBAL_NOT_FOUND_LAYOUT
            self._log_.debug(lambda: f"Update Location Callback: Updated Sidebar")
            content = self.GLOBAL_NOT_FOUND_LAYOUT
            self._log_.debug(lambda: f"Update Location Callback: Updated Content")
        return anchor, location.dict(), description, navigation, sidebar, content, loading, reloading

    @serverside_callback(
        Output("GLOBAL_LOCATION_ID", "pathname"),
        Output("GLOBAL_LOCATION_STORAGE_ID", "data"),
        Input("GLOBAL_BACKWARD_BUTTON_ID", "n_clicks"),
        State("GLOBAL_LOCATION_STORAGE_ID", "data")
    )
    def _global_backward_location_callback_(self, clicks: int, location: dict):
        if not clicks: raise PreventUpdate
        self._log_.debug(lambda: f"Backward Location Callback: Clicks = {clicks}")
        location = LocationAPI(**location)
        path = location.backward(step=True)
        if not path:
            self._log_.debug(lambda: "Backward Location Callback: No Backward Path Available")
            raise PreventUpdate
        self._log_.debug(lambda: f"Backward Location Callback: Navigating to {path}")
        return path, location.dict()

    @clientside_callback(
        Input("GLOBAL_REFRESH_BUTTON_ID", "n_clicks"),
        Input("GLOBAL_REFRESH_TRIGGER_ID", "data")
    )
    def _global_refresh_location_callback_(self):
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
        }
        """

    @serverside_callback(
        Output("GLOBAL_LOCATION_ID", "pathname"),
        Output("GLOBAL_LOCATION_STORAGE_ID", "data"),
        Input("GLOBAL_FORWARD_BUTTON_ID", "n_clicks"),
        State("GLOBAL_LOCATION_STORAGE_ID", "data")
    )
    def _global_forward_location_callback_(self, clicks: int, location: dict):
        if not clicks: raise PreventUpdate
        self._log_.debug(lambda: f"Forward Location Callback: Clicks = {clicks}")
        location = LocationAPI(**location)
        path = location.forward(step=True)
        if not path:
            self._log_.debug(lambda: "Forward Location Callback: No Forward Path Available")
            raise PreventUpdate
        self._log_.debug(lambda: f"Forward Location Callback: Navigating to {path}")
        return path, location.dict()

    def _global_collapse_button_callback_(self, name: str, was_open: bool, classname: str = None):
        is_open = not was_open
        self._log_.debug(lambda: f"{name} Callback: {'Expanding' if is_open else 'Collapsing'}")
        if not classname: return is_open
        elif is_open: classname = classname.replace("down", "up")
        else: classname = classname.replace("up", "down")
        return is_open, classname

    @serverside_callback(
        Output("GLOBAL_SIDEBAR_COLLAPSE_ID", "is_open"),
        Input("GLOBAL_SIDEBAR_BUTTON_ID", "n_clicks"),
        State("GLOBAL_SIDEBAR_COLLAPSE_ID", "is_open")
    )
    def _global_sidebar_button_callback_(self, clicks: int, was_open: bool):
        if not clicks: raise PreventUpdate
        return self._global_collapse_button_callback_(name="Sidebar", was_open=was_open)

    @serverside_callback(
        Output("GLOBAL_CONTACTS_COLLAPSE_ID", "is_open"),
        Output("GLOBAL_CONTACTS_ARROW_ID", "className"),
        Input("GLOBAL_CONTACTS_BUTTON_ID", "n_clicks"),
        State("GLOBAL_CONTACTS_COLLAPSE_ID", "is_open"),
        State("GLOBAL_CONTACTS_ARROW_ID", "className")
    )
    def _global_contacts_button_callback_(self, clicks: int, was_open: bool, classname: str):
        if not clicks: raise PreventUpdate
        return self._global_collapse_button_callback_(name="Contacts", was_open=was_open, classname=classname)

    def _global_import_snapshot_callback_(self, contents: str, filename: str, prop: str):
        if not contents: raise PreventUpdate
        try:
            _, b64 = contents.split(",", 1)
            decoded = base64.b64decode(b64)
            payload = json.loads(decoded.decode("utf-8"))
        except Exception as exc:
            self._log_.warning(lambda: f"Import Snapshot: Failed to Parse {filename}")
            self._log_.error(lambda: f"{exc}")
            raise PreventUpdate
        snapshot_page = payload.get("page")
        components = payload.get("components") or []
        wanted = {json.dumps(c["id"], sort_keys=True): c["value"]
                  for c in components if c.get("prop") == prop and isinstance(c.get("id"), dict)}
        outs = []
        for entry in (self.ctx.outputs_list or []):
            outs.extend(entry if isinstance(entry, list) else [entry])
        values = []
        for out in outs:
            cid = out.get("id")
            if not isinstance(cid, dict):
                values.append(dash.no_update)
                continue
            if snapshot_page and cid.get("page") != snapshot_page:
                values.append(dash.no_update)
                continue
            key = json.dumps(cid, sort_keys=True)
            values.append(wanted.get(key, dash.no_update))
        return values

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "data"}, "data"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_data_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "data")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "value"}, "value"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_value_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "value")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "input"}, "input"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_input_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "input")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "filter"}, "filter"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_filter_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "filter")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "date"}, "date"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_date_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "date")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "checked"}, "checked"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_checked_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "checked")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "start_date"}, "start_date"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_start_date_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "start_date")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "end_date"}, "end_date"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_end_date_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "end_date")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "options"}, "options"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_options_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "options")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "disabled"}, "disabled"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_disabled_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "disabled")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "is_open"}, "is_open"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_is_open_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "is_open")

    @serverside_callback(
        Output({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "active_tab"}, "active_tab"),
        Input("GLOBAL_IMPORT_UPLOAD_ID", "contents"),
        State("GLOBAL_IMPORT_UPLOAD_ID", "filename")
    )
    def _global_import_snapshot_active_tab_callback_(self, contents: str, filename: str):
        return self._global_import_snapshot_callback_(contents, filename, "active_tab")

    @serverside_callback(
        Output("GLOBAL_EXPORT_DOWNLOAD_ID", "data"),
        Input("GLOBAL_EXPORT_ID", "n_clicks"),
        State("GLOBAL_LOCATION_ID", "pathname"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "data"}, "data"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "value"}, "value"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "input"}, "input"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "filter"}, "filter"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "date"}, "date"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "checked"}, "checked"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "start_date"}, "start_date"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "end_date"}, "end_date"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "options"}, "options"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "disabled"}, "disabled"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "is_open"}, "is_open"),
        State({"page": dash.ALL, "type": dash.ALL, "name": dash.ALL, "portable": "active_tab"}, "active_tab")
    )
    def _global_export_snapshot_callback_(self, clicks: int, path: str, *_):
        if not clicks: raise PreventUpdate
        if not path: raise PreventUpdate
        endpoint = self.endpointize(path=path, relative=False)
        state_entries = []
        for entry in (self.ctx.states_list or []):
            state_entries.extend(entry if isinstance(entry, list) else [entry])
        components = []
        for s in state_entries:
            cid = s.get("id")
            if not isinstance(cid, dict):
                continue
            if cid.get("page") != endpoint:
                continue
            prop = s.get("property")
            if not prop:
                continue
            components.append({"id": cid, "prop": prop, "value": s.get("value")})
        payload = {"page": endpoint, "components": components}
        filename = f"snapshot-{endpoint.strip('/').replace('/', '-') or 'root'}.json"
        return dcc.send_string(json.dumps(payload, indent=2, sort_keys=True), filename=filename)

    def _global_clean_storage_callback_(self, clicks: int, trigger: dict, name: str, storage: str):
        if not clicks and not trigger: raise PreventUpdate
        self._log_.debug(lambda: f"Clean {storage.title()} Callback: Cleaned {name} Storage")
        return dict()

    @serverside_callback(
        Output("GLOBAL_LOADING_TRIGGER_ID", "data"),
        Output("GLOBAL_ROUTING_STORAGE_ID", "data"),
        Output("GLOBAL_RELOADING_TRIGGER_ID", "data"),
        Output("GLOBAL_UNLOADING_TRIGGER_ID", "data"),
        Output("GLOBAL_MEMORY_STORAGE_ID", "data"),
        Output("GLOBAL_REFRESH_TRIGGER_ID", "data"),
        Input("GLOBAL_CLEAN_MEMORY_BUTTON_ID", "n_clicks"),
        Input("GLOBAL_CLEAN_MEMORY_TRIGGER_ID", "data"),
        State("GLOBAL_MEMORY_STORAGE_ID", "storage_type"),
        State("GLOBAL_REFRESH_TRIGGER_ID", "data")
    )
    def _global_clean_memory_callback_(self, clicks: int, trigger: dict, storage: str, refresh: dict):
        loading = self._global_clean_storage_callback_(clicks=clicks, trigger=trigger, name="Loading", storage=storage)
        routing = self._global_clean_storage_callback_(clicks=clicks, trigger=trigger, name="Routing", storage=storage)
        reloading = self._global_clean_storage_callback_(clicks=clicks, trigger=trigger, name="Reloading", storage=storage)
        unloading = self._global_clean_storage_callback_(clicks=clicks, trigger=trigger, name="Unloading", storage=storage)
        memory = self._global_clean_storage_callback_(clicks=clicks, trigger=trigger, name="Memory", storage=storage)
        refresh = TriggerAPI(**refresh)
        return loading, routing, reloading, unloading, memory, refresh.trigger().dict()

    @serverside_callback(
        Output("GLOBAL_LOCATION_STORAGE_ID", "data"),
        Output("GLOBAL_SESSION_STORAGE_ID", "data"),
        Output("GLOBAL_CLEAN_MEMORY_TRIGGER_ID", "data"),
        Input("GLOBAL_CLEAN_SESSION_BUTTON_ID", "n_clicks"),
        Input("GLOBAL_CLEAN_SESSION_TRIGGER_ID", "data"),
        State("GLOBAL_SESSION_STORAGE_ID", "storage_type"),
        State("GLOBAL_CLEAN_MEMORY_TRIGGER_ID", "data")
    )
    def _global_clean_session_callback_(self, clicks: int, trigger: dict, storage: str, memory: dict):
        location = self._global_clean_storage_callback_(clicks=clicks, trigger=trigger, name="Location", storage=storage)
        session = self._global_clean_storage_callback_(clicks=clicks, trigger=trigger, name="Session", storage=storage)
        memory = TriggerAPI(**memory)
        return location, session, memory.trigger().dict()

    @serverside_callback(
        Output("GLOBAL_LOCAL_STORAGE_ID", "data"),
        Output("GLOBAL_CLEAN_SESSION_TRIGGER_ID", "data"),
        Input("GLOBAL_CLEAN_LOCAL_BUTTON_ID", "n_clicks"),
        Input("GLOBAL_CLEAN_LOCAL_TRIGGER_ID", "data"),
        State("GLOBAL_LOCAL_STORAGE_ID", "storage_type"),
        State("GLOBAL_CLEAN_SESSION_TRIGGER_ID", "data")
    )
    def _global_clean_local_callback_(self, clicks: int, trigger: dict, storage: str, session: dict):
        local = self._global_clean_storage_callback_(clicks=clicks, trigger=trigger, name="Local", storage=storage)
        session = TriggerAPI(**session)
        return local, session.trigger().dict()

    @serverside_callback(
        Output("GLOBAL_TERMINAL_COLLAPSE_ID", "is_open"),
        Output("GLOBAL_TERMINAL_ARROW_ID", "className"),
        Input("GLOBAL_TERMINAL_BUTTON_ID", "n_clicks"),
        State("GLOBAL_TERMINAL_COLLAPSE_ID", "is_open"),
        State("GLOBAL_TERMINAL_ARROW_ID", "className")
    )
    def _global_terminal_button_callback_(self, clicks: int, was_open: bool, classname: str):
        if not clicks: raise PreventUpdate
        return self._global_collapse_button_callback_(name="Terminal", was_open=was_open, classname=classname)

    @serverside_callback(
        Output("GLOBAL_TERMINAL_ID", "children"),
        Input("GLOBAL_TERMINAL_INTERVAL_ID", "n_intervals"),
        State("GLOBAL_TERMINAL_ID", "children")
    )
    def _global_terminal_stream_callback_(self, _, terminal: list[Component]):
        logs = self._log_.web.stream()
        if not logs: raise PreventUpdate
        terminal = terminal or []
        terminal.extend(logs)
        return terminal[-self._terminal_:]

    def ids(self) -> None:
        pass

    def pages(self) -> None:
        pass

    def run(self):
        return self.app.run(
            host=self._host_,
            port=self._port_,
            proxy=self._proxy_,
            debug=self._debug_,
            jupyter_mode="external",
            jupyter_server_url=self._domain_url_
        )

    def mount(self):
        app = FastAPI()
        app.mount(self._endpoint_, WSGIMiddleware(self.app.server))
        return app
