import dash
from dash import html, dcc
from pathlib import PurePath, PurePosixPath
from abc import ABC, abstractmethod

from Library.Logging import HandlerAPI
from Library.Utility import inspect_file, inspect_path, inspect_file_path, traceback_calling_module

class AppAPI(ABC):

    LAYOUT_ID = {"type": "div", "index": "layout"}
    HEADER_ID = {"type": "div", "index": "header"}
    CONTENT_ID = {"type": "div", "index": "content"}
    FOOTER_ID = {"type": "div", "index": "footer"}
    HIDDEN_ID = {"type": "div", "index": "hidden"}

    LOCATION_ID = {"type": "location", "index": "page"}
    SELECTED_ID = {"type": "div", "index": "selected"}
    INTERVAL_ID = {"type": "interval", "index": "interval"}
    SESSION_ID = {"type": "storage", "index": "session"}

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
        self._links_: dict[str, dict] = {}

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

        self._init_layout_()
        self._log_.info(lambda: "Initialized Layout")

        self._init_callbacks_()
        self._log_.info(lambda: "Initialized Callbacks")

    def _init_app(self):

        self.app = dash.Dash(
            name=self.name,
            title=self.title,
            assets_folder=self.assets,
            url_base_pathname=self.endpoint,
            suppress_callback_exceptions=True,
            prevent_initial_callbacks=True
        )

    def _init_status_(self) -> None:

        self.NOT_FOUND_LAYOUT = html.Div([
            html.Img(src=self.app.get_asset_url("404.png"), className="status-layout-image", alt="Resource Not Found"),
            html.H2("Resource Not Found", className="status-layout-title"),
            html.P("Unable to find the resource you are looking for.", className="status-layout-text"),
        ], className="status-layout status-layout-404")

        self.LOADING_LAYOUT = html.Div([
            html.Img(src=self.app.get_asset_url("loading.gif"), className="status-layout-image", alt="Loading"),
            html.H2("Loading...", className="status-layout-title"),
            html.P("Please wait a moment.", className="status-layout-text"),
        ],className="status-layout status-layout-loading")

        self.MAINTENANCE_LAYOUT = html.Div([
            html.Img(src=self.app.get_asset_url("maintenance.png"), className="status-layout-image", alt="Under Maintenance"),
            html.H2("Resource Under Maintenance", className="status-layout-title"),
            html.P("This resource is temporarily down for maintenance.", className="status-layout-text"),
            html.P("Please try again later.", className="status-layout-text"),
        ], className="status-layout status-layout-maintenance")

        self.DEVELOPMENT_LAYOUT = html.Div([
            html.Img(src=self.app.get_asset_url("development.png"), className="status-layout-image", alt="Work in Progress"),
            html.H2("Work in progress", className="status-layout-title"),
            html.P("This resource is currently under development.", className="status-layout-text"),
            html.P("Please try again later.", className="status-layout-text"),
        ], className="status-layout status-layout-development")

    def _init_header_(self) -> html.Div:

        return html.Div([
            html.Div([
                html.Div([html.Img(src=self.app.get_asset_url("logo.png"), className="header-image")], className="header-logo"),
                html.Div([html.H1(self.name, className="header-title"), html.H4(self.team, className="header-team")], className="header-title-team"),
                html.Div(self.description, id=self.SELECTED_ID, className="header-description")
            ], className="header-information-block"),
            html.Div([html.A(link["button"], href=endpoint, className="header-selection") for endpoint, link in self._links_.items()
            ], className="header-selection-block")
        ], id=self.HEADER_ID, className="header")

    def _init_content_(self) -> html.Div:

        return html.Div(
            [self.LOADING_LAYOUT],
            id=self.CONTENT_ID,
            className="content"
        )

    def _init_footer_(self) -> html.Div:

        return html.Div([
            html.A(
                f"Contact: {self.contact}",
                href=f"mailto:{self.contact}",
                className="footer-contact"
            )
        ], id=self.FOOTER_ID, className="footer")

    def _init_hidden_(self) -> html.Div:

        return html.Div(id=self.HIDDEN_ID, children=[
            dcc.Interval(id=self.INTERVAL_ID, interval=1000, n_intervals=0, disabled=False),
            dcc.Store(id=self.SESSION_ID, storage_type="memory"),
            dcc.Location(id=self.LOCATION_ID, refresh=False)
        ])

    def _init_layout_(self):

        self._init_status_()
        self._log_.debug(lambda: "Loaded Status Layout")
        self.layout()
        self._log_.debug(lambda: "Loaded Specific Layout")
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
            dash.Output(self.CONTENT_ID, "children", allow_duplicate=True),
            dash.Input(self.LOCATION_ID, "pathname")
        )
        def _location_callback_(anchor: str):
            self._log_.debug(lambda: f"Location Callback: Received Anchor = {anchor}")
            anchor = inspect_file_path(anchor, header=True, builder=PurePosixPath)
            self._log_.debug(lambda: f"Location Callback: Parsed Anchor = {anchor}")
            link = self._links_.get(anchor, None)
            self._log_.debug(lambda: f"Location Callback: Link Found = {link is not None}")
            layout = link["layout"] if (link is not None) else self.NOT_FOUND_LAYOUT
            description = link["description"] if (link is not None and self.description is not None) else dash.no_update
            return anchor, description, layout

        self.callbacks()

    def link(self, path: str, button: str, description: str, layout):
        self._log_.debug(lambda: f"Link Definition: Path = {path}")
        path = inspect_file(path, header=True, builder=PurePosixPath).name
        anchor: str = inspect_path(self.anchor / path)
        self._log_.debug(lambda: f"Link Definition: Anchor = {anchor}")
        endpoint: str = inspect_path(self.anchor / path, footer=True)
        self._log_.debug(lambda: f"Link Definition: Endpoint = {endpoint}")
        order = len(self._links_)
        self._log_.debug(lambda: f"Link Definition: Order = {order}")
        self._links_[anchor] = {
            "order": order,
            "button": button,
            "description": description,
            "anchor": anchor,
            "endpoint": endpoint,
            "layout": layout
        }
        self._log_.info(lambda: f"Defined Link: Anchor = {anchor}")

    @abstractmethod
    def layout(self):
        raise NotImplementedError

    @abstractmethod
    def callbacks(self):
        raise NotImplementedError

    def run(self):
        return self.app.run(port=self.port, debug=self.debug)
