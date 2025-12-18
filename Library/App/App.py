import dash
from dash import dcc, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from pathlib import PurePosixPath

from Library.Logging import *
from Library.App import *
from Library.Utility.HTML import *
from Library.Utility.Path import *

def callback(*args, **kwargs):
    def decorator(func):
        func._callback_ = True
        func._callback_args_ = args
        func._callback_kwargs_ = kwargs
        return func
    return decorator

class AppAPI:

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
    MEMORY_STORAGE_ID: dict = {"type": "storage", "index": "memory"}
    SESSION_STORAGE_ID: dict = {"type": "storage", "index": "session"}
    LOCAL_STORAGE_ID: dict = {"type": "storage", "index": "local"}

    NOT_FOUND_LAYOUT: Component = None
    LOADING_LAYOUT: Component = None
    MAINTENANCE_LAYOUT: Component = None
    DEVELOPMENT_LAYOUT: Component = None
    NOT_INDEXED_LAYOUT: Component = None

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

        self._init_navigation_()
        self._log_.debug(lambda: "Initialized Navigation")

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

        self.NOT_FOUND_LAYOUT: Component = DefaultLayoutAPI(
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
                page.navigation = page.parent.navigation
                continue

            navigation_items: list = []

            if page.parent is not None:
                navigation_items.append(dbc.ButtonGroup(dbc.Button(f"⭰ {page.parent.button}", href=page.parent._anchor_, className="header-navigation-button"), className="header-navigation-group"))

            for member in page.family:
                navigation_group: list = [
                    dbc.Button(member.button, href=member._anchor_, className="header-navigation-button"),
                    new_tab_button(href=member._anchor_, className="header-navigation-button-tab")
                ]
                if member.children:
                    dropdown_group = []
                    for subchild in member.children:
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
                ButtonContainerAPI(background="primary", border="white", elements=[
                    ButtonAPI(key=self._PAGE_BACKWARD_ID_, stylename="bi bi-arrow-left"),
                    ButtonAPI(key=self._PAGE_REFRESH_ID_, stylename="bi bi-arrow-repeat"),
                    ButtonAPI(key=self._PAGE_FORWARD_ID_, stylename="bi bi-arrow-right")
                ], stylename="header-history-block").build()
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
            ButtonAPI(key=self._CONTACTS_BUTTON_ID_, label=[
                IconAPI(icon="bi bi-caret-down-fill", key=self._CONTACTS_ARROW_ID_),
                TextAPI(text="  Contacts  "),
                IconAPI(icon="bi bi-question-circle")
            ], background="primary", border="white").build(),
            ButtonAPI(key=self._TERMINAL_BUTTON_ID_, label=[
                IconAPI(icon="bi bi-terminal"),
                TextAPI(text="  Terminal  "),
                IconAPI(icon="bi bi-caret-down-fill", key=self._TERMINAL_ARROW_ID_)
            ], background="primary", border="white").build(),
            dbc.Collapse(dbc.Card(dbc.CardBody(html.Div(self._init_contacts_(), id=self._CONTACTS_CONTENT_ID_)), className="footer-panel footer-panel-left"), id=self._CONTACTS_COLLAPSE_ID_, is_open=False),
            dbc.Collapse(dbc.Card(dbc.CardBody(html.Pre([], id=self._TERMINAL_CONTENT_ID_)), color="dark", inverse=True, className="footer-panel footer-panel-right"), id=self._TERMINAL_COLLAPSE_ID_, is_open=False)
        ], id=self._FOOTER_ID_, className="footer")

    def _init_hidden_(self) -> html.Div:

        return html.Div([
            dcc.Interval(id=self.INTERVAL_ID, interval=1000, n_intervals=0, disabled=False),
            dcc.Store(id=self.HISTORY_STORAGE_ID, storage_type="session", data=HistorySessionAPI().dict()),
            dcc.Store(id=self.MEMORY_STORAGE_ID, storage_type="memory", data=dict()),
            dcc.Store(id=self.SESSION_STORAGE_ID, storage_type="session", data=dict()),
            dcc.Store(id=self.LOCAL_STORAGE_ID, storage_type="local", data=dict()),
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

        for cls in reversed(type(self).mro()):
            if cls is object:
                continue
            for name, func in cls.__dict__.items():
                if not callable(func):
                    continue
                if not getattr(func, "_callback_", False):
                    continue
                bound = getattr(self, name)
                callback_args = getattr(func, "_callback_args_")
                callback_kwargs = getattr(func, "_callback_kwargs_")
                self.app.callback(*callback_args, **callback_kwargs)(bound)
                self._log_.debug(lambda: f"Loaded Callback: {name}")

    @callback(
        dash.Output(_PAGE_LOCATION_ID_, "pathname", allow_duplicate=True),
        dash.Output(_PAGE_SELECTED_ID_, "children", allow_duplicate=True),
        dash.Output(_PAGE_NAVIGATION_ID_, "children", allow_duplicate=True),
        dash.Output(_CONTENT_ID_, "children", allow_duplicate=True),
        dash.Input(_PAGE_LOCATION_ID_, "pathname"),
        prevent_initial_call=False
    )
    def _update_location_callback_(self, path: str):
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
            content = self.NOT_FOUND_LAYOUT
        return anchor, description, navigation, content

    @callback(
        dash.Output(HISTORY_STORAGE_ID, "data", allow_duplicate=True),
        dash.Input(_PAGE_LOCATION_ID_, "pathname"),
        dash.State(HISTORY_STORAGE_ID, "data"),
        prevent_initial_call=True
    )
    def _update_history_callback_(self, path, history):
        history = HistorySessionAPI(**history)
        history.Register(path)
        return history.dict()

    @callback(
        dash.Output(_PAGE_LOCATION_ID_, "pathname", allow_duplicate=True),
        dash.Input(_PAGE_BACKWARD_ID_, "n_clicks"),
        dash.State(HISTORY_STORAGE_ID, "data"),
        prevent_initial_call=True
    )
    def _backward_history_callback_(self, clicks, history):
        if clicks is None: raise PreventUpdate
        history = HistorySessionAPI(**history)
        path = history.Backward()
        return path if path else dash.no_update

    @callback(
        dash.Output(_PAGE_LOCATION_ID_, "pathname", allow_duplicate=True),
        dash.Input(_PAGE_REFRESH_ID_, "n_clicks"),
        dash.State(_PAGE_LOCATION_ID_, "pathname"),
        prevent_initial_call=True
    )
    def _refresh_history_callback_(self, clicks, path):
        if clicks is None: raise PreventUpdate
        return path

    @callback(
        dash.Output(_PAGE_LOCATION_ID_, "pathname", allow_duplicate=True),
        dash.Input(_PAGE_FORWARD_ID_, "n_clicks"),
        dash.State(HISTORY_STORAGE_ID, "data"),
        prevent_initial_call=True
    )
    def _forward_history_callback_(self, clicks, history):
        if clicks is None: raise PreventUpdate
        history = HistorySessionAPI(**history)
        path = history.Forward()
        return path if path else dash.no_update

    @staticmethod
    def _collapsable_button_callback_(was_open: bool, classname: str):
        is_open = not was_open
        if is_open: classname = classname.replace("down", "up")
        else: classname = classname.replace("up", "down")
        return is_open, classname

    @callback(
        dash.Output(_CONTACTS_COLLAPSE_ID_, "is_open", allow_duplicate=True),
        dash.Output(_CONTACTS_ARROW_ID_, "className", allow_duplicate=True),
        dash.Input(_CONTACTS_BUTTON_ID_, "n_clicks"),
        dash.State(_CONTACTS_COLLAPSE_ID_, "is_open"),
        dash.State(_CONTACTS_ARROW_ID_, "className"),
        prevent_initial_call=True
    )
    def _contacts_button_callback_(self, clicks, was_open: bool, classname: str):
        if clicks is None: raise PreventUpdate
        is_open, classname = self._collapsable_button_callback_(was_open=was_open, classname=classname)
        self._log_.debug(lambda: f"Contacts Callback: {'Expanding' if is_open else 'Collapsing'}")
        return is_open, classname

    @callback(
        dash.Output(_TERMINAL_COLLAPSE_ID_, "is_open", allow_duplicate=True),
        dash.Output(_TERMINAL_ARROW_ID_, "className", allow_duplicate=True),
        dash.Input(_TERMINAL_BUTTON_ID_, "n_clicks"),
        dash.State(_TERMINAL_COLLAPSE_ID_, "is_open"),
        dash.State(_TERMINAL_ARROW_ID_, "className"),
        prevent_initial_call=True
    )
    def _terminal_button_callback_(self, clicks, was_open: bool, classname: str):
        if clicks is None: raise PreventUpdate
        is_open, classname = self._collapsable_button_callback_(was_open=was_open, classname=classname)
        self._log_.debug(lambda: f"Terminal Callback: {'Expanding' if is_open else 'Collapsing'}")
        return is_open, classname

    @callback(
        dash.Output(_TERMINAL_CONTENT_ID_, "children", allow_duplicate=True),
        dash.Input(INTERVAL_ID, "n_intervals"),
        dash.State(_TERMINAL_CONTENT_ID_, "children"),
        prevent_initial_call=True
    )
    def _terminal_stream_callback_(self, _, terminal):
        logs = self._log_.web.stream()
        if not logs: raise PreventUpdate
        terminal.extend(logs)
        return terminal

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

    def index(self, endpoint: str, page: PageAPI) -> None:
        self._pages_[endpoint] = page

    def link(self, page: PageAPI):
        relative_path: PurePath = inspect_file(page.path, header=True, builder=PurePosixPath)
        self._log_.debug(lambda: f"Page Linking: Relative Path = {relative_path}")
        relative_anchor = self.anchorize(path=relative_path)
        self._log_.debug(lambda: f"Page Linking: Relative Anchor = {relative_anchor}")
        relative_endpoint = self.endpointize(path=relative_path)
        self._log_.debug(lambda: f"Page Linking: Relative Endpoint = {relative_endpoint}")
        intermediate_alias: PurePath = inspect_file("/", builder=PurePosixPath)
        intermediate_parent: PageAPI = self.locate(endpoint=self.endpointize(path=intermediate_alias))
        for part in relative_path.parts[1:-1]:
            intermediate_path: PurePath = inspect_file(part, header=True, builder=PurePosixPath)
            intermediate_alias = intermediate_alias / intermediate_path.name
            self._log_.debug(lambda: f"Page Linking: Intermediate Path = {intermediate_alias}")
            intermediate_anchor = self.anchorize(path=intermediate_alias)
            self._log_.debug(lambda: f"Page Linking: Intermediate Anchor = {intermediate_anchor}")
            intermediate_endpoint = self.endpointize(path=intermediate_alias)
            self._log_.debug(lambda: f"Page Linking: Intermediate Endpoint = {intermediate_endpoint}")
            intermediate_page: PageAPI = self.locate(endpoint=intermediate_endpoint)
            if not intermediate_page:
                intermediate_page = PageAPI(
                    app=self,
                    path=inspect_path(intermediate_alias),
                    description="Resource Not Indexed",
                    indexed=False,
                    layout=self.NOT_INDEXED_LAYOUT
                )
                self._log_.debug(lambda: f"Page Linking: Created Intermediate Page = {intermediate_endpoint}")
            intermediate_page.anchor = intermediate_anchor
            intermediate_page.endpoint = intermediate_endpoint
            self.index(endpoint=intermediate_endpoint, page=intermediate_page)
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
            self.index(endpoint=relative_endpoint, page=page)
            self._log_.info(lambda: f"Page Linking: Linked Relative Page = {page}")
        page.attach(parent=intermediate_parent)

    def pages(self):
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
