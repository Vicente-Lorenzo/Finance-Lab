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

    NOT_FOUND_LAYOUT = html.Div("Error 404: Resource Not Found")

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

    def _init_layout_(self):

        self._links_: dict[str, dict] = {}
        self.layout()

        header = html.Div(id=AppAPI.HEADER_ID, children=[
            html.Div(children=[
                html.Div(children=[html.Img(src=self.app.get_asset_url("logo.png"), className="image")], className="logo"),
                html.Div(children=[
                    html.H1(
                        children=self.name,
                        style={
                            "display": "flex",
                            "flex-direction": "row",
                            "justify-content": "flex-start",
                            "font-size": "32px",
                            "font-weight": "bold",
                            "margin": "0px 0px 0px 0px"
                        }
                    ),
                    html.H4(
                        children=self.team,
                        style={
                            "display": "flex",
                            "flex-direction": "row",
                            "justify-content": "flex-start",
                            "font-size": "18px",
                            "font-weight": "normal",
                            "margin": "0px 0px 0px 0px"
                        }
                    )
                ], style={
                    "display": "flex",
                    "flex-direction": "column",
                    "justify-content": "flex-start",
                    "padding": "0px 15px 0px 0px",
                    "margin": "auto auto auto auto"
                }),
                html.Div(id=AppAPI.SELECTED_ID, children=self.description, style={
                    "display": "flex",
                    "flex-direction": "row",
                    "justify-content": "flex-start",
                    "font-size": "24px",
                    "font-weight": "normal",
                    "border-left": "1px solid black",
                    "padding": "0px 0px 0px 15px",
                    "margin": "auto auto auto auto"
                })
            ], style={
                "display": "flex",
                "flex-direction": "row",
                "justify-content": "flex-start"
            }),
            html.Div(children=[html.A(children=link["button"], href=endpoint, className="selection") for endpoint, link in self._links_.items()], className="selector")
        ], style={
            "display": "flex",
            "flex-direction": "row",
            "align-items": "center",
            "justify-content": "space-between",
            "padding": "5px 5px 5px 5px",
            "border-bottom": "2px solid black"
        })

        content = html.Div(
            id=AppAPI.CONTENT_ID,
            children=[]
        )

        footer = html.Div(id=AppAPI.FOOTER_ID, children=[
            html.A(children=f"Contact: {self.contact}", href=f"mailto:{self.contact}", style={
                "font-weight": "normal"
            })
        ], style={
            "right": "0",
            "bottom": "0",
            "position": "fixed",
            "border-top": "2px solid black",
            "border-left": "2px solid black",
            "margin": "auto auto auto auto",
            "padding": "5px 5px 5px 5px"
        })

        hidden = html.Div(id=AppAPI.HIDDEN_ID, children=[
            dcc.Interval(id=AppAPI.INTERVAL_ID, interval=1000, n_intervals=0, disabled=False),
            dcc.Store(id=AppAPI.SESSION_ID, storage_type="memory"),
            dcc.Location(id=AppAPI.LOCATION_ID, refresh=False)
        ], style={})

        self.app.layout = html.Div(
            id=AppAPI.LAYOUT_ID,
            children=[header, content, footer, hidden],
            style={"font-family": "BNPP Sans"}
        )

        self._links_ = dict(sorted(self._links_.items(), key=lambda item: item[1]["order"]))

    def _init_callbacks_(self):

        @self.app.callback(
            dash.Output(AppAPI.LOCATION_ID, "pathname", allow_duplicate=True),
            dash.Output(AppAPI.SELECTED_ID, "children", allow_duplicate=True),
            dash.Output(AppAPI.CONTENT_ID, "children", allow_duplicate=True),
            dash.Input(AppAPI.LOCATION_ID, "pathname")
        )
        def _location_callback_(anchor: str):
            self._log_.debug(lambda: f"Location Callback: Received Anchor = {anchor}")
            anchor = inspect_file_path(anchor, header=True, builder=PurePosixPath)
            self._log_.debug(lambda: f"Location Callback: Parsed Anchor = {anchor}")
            link = self._links_.get(anchor, None)
            self._log_.debug(lambda: f"Location Callback: Link Found = {link is not None}")
            layout = link["layout"] if (link is not None) else AppAPI.NOT_FOUND_LAYOUT
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
        return self.app.run_server(port=self.port, debug=self.debug)
