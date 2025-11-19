import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import dash
from dash import html, dcc, page_container
from dash.exceptions import PreventUpdate
from dash import bootstrap_components as dbc

from Library.Logging import HandlerAPI
from Library.Utility import inspect_file, inspect_file_path, traceback_regex_module

@dataclass(kw_only=True)
class AppAPI(ABC):

    LAYOUT_ID = {"type": "div", "index": "layout"}
    HEADER_ID = {"type": "div", "index": "header"}
    CONTENT_ID = {"type": "div", "index": "content"}
    FOOTER_ID = {"type": "div", "index": "footer"}

    SELECTED_ID = {"type": "div", "index": "selected"}
    INTERVAL_ID = {"type": "interval", "index": "interval"}
    SESSION_ID = {"type": "storage", "index": "session"}
    LOCATION_ID = {"type": "location", "index": "page"}

    App: dash.Dash = field(init=False)

    Title: str = field(init=True, default="<Insert Title>")
    Name: str = field(init=True, default="<Insert Name>")
    Team: str = field(init=True, default="<Insert Team>")
    Description: str = field(init=True, default="<Insert Description>")
    Contact: str = field(init=True, default="<Insert Contact>")
    Pages: bool = field(init=True, default=False)

    Port: int = field(init=True, default=8050)
    Debug: bool = field(init=True, default=False)

    Module: Path = field(init=False, default=None)
    Anchor: str = field(init=False, default=None)

    def __post_init__(self):

        self._log_: HandlerAPI = HandlerAPI()

        self._links_: dict = {}
        self._counter_: int = 0

        if jhub.is_service():
            self._log_.debug(lambda: "Configuring for Remove Prod")
            api = os.environ.get("JUPYTERHUB_USER").replace("-team", "")
            self._log_.debug(lambda: f"Defined Profile API: {api}")
            directory = inspect_file_path(traceback_regex_module(pattern=r"^team/team-api/[^/]+/__init__\.py$").name)
            self._log_.debug(lambda: f"Defined Directory: {directory}")
            endpoint = f"/services/{api}/{directory}/"
            self._log_.debug(lambda: f"Defined Endpoint: {endpoint}")
            self.Module = inspect_file(endpoint, header=True)
            self.Anchor = inspect_file_path(endpoint, header=True, footer=True)
        elif jhub.is_jupyterhub():
            self._log_.debug(lambda: "Configuring for Remote Dev")
            user = os.environ.get('JUPYTERHUB_USER')
            server = os.environ.get('JUPYTERHUB_SERVER_NAME')
            self._log_.debug(lambda: f"Defined User: {user}")
            self._log_.debug(lambda: f"Defined Server: {server}")
            endpoint = f"/user/{user}/server/{server}/proxy/{self.Port}/"
            self._log_.debug(lambda: f"Defined Endpoint: {endpoint}")
            self.Module = inspect_file(endpoint, header=True)
            self.Anchor = inspect_file_path(endpoint, header=True, footer=True)
        else:
            self._log_.debug(lambda: "Configuring for Local Dev")
            endpoint = "/"
            self._log_.debug(lambda: f"Defined Endpoint: {endpoint}")
            self.Module = inspect_file(endpoint, header=True)
            self.Anchor = inspect_file_path(endpoint, header=True, footer=True)

        self._log_.debug(lambda: f"Defined Module: {self.Module}")
        self._log_.debug(lambda: f"Defined Anchor: {self.Anchor}")

        self._init_app()
        self._log_.debug(lambda: "Initialized App")

        self._init_layout()
        self._log_.debug(lambda: "Initialized Layout")

        self._init_callbacks()
        self._log_.debug(lambda: "Initialized Callbacks")

    def _init_app(self):
        self.App = dash.Dash(
            name=__name__,
            title=self.Title,
            use_pages=self.Pages,
            pages_folder="",
            requests_pathname_prefix=self.Anchor,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            update_title="",
            suppress_callback_exceptions=True,
            prevent_initial_callbacks=True
        )

    def _init_layout(self):

        self.layout()
        self._registry_()

        header = html.Div(id=AppAPI.HEADER_ID, children=[
            html.Div(children=[
                html.Div(children=html.Img(src="./assets/logo.png", className="image"), className="logo"),
                html.Div(children=[
                    html.H1(
                        children=self.Name,
                        style={
                            "display": "flex",
                            "flex-direction": "row",
                            "justify-content": "flex-start",
                            "font-size": "32px",
                            "font-weight": "bold",
                            "margin": "0px 0px 0px 0px"
                        },
                    ),
                    html.H4(
                        children=self.Team,
                        style={
                            "display": "flex",
                            "flex-direction": "row",
                            "justify-content": "flex-start",
                            "font-size": "18px",
                            "font-weight": "normal",
                            "margin": "0px 0px 0px 0px"
                        },
                    )
                ], style={
                    "display": "flex",
                    "flex-direction": "column",
                    "justify-content": "flex-start",
                    "padding": "0px 15px 0px 0px",
                    "margin": "auto auto auto auto"
                }),
                html.Div(id=AppAPI.SELECTED_ID, children=self.Description, style={
                    "display": "flex",
                    "flex-direction": "row",
                    "justify-content": "flex-start",
                    "font-size": "24px",
                    "font-weight": "normal",
                    "border-left": "10px solid black",
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
            children=page_container
        )

        footer = html.Div(id=AppAPI.FOOTER_ID, children=[
            html.A(children=f"Contact: {self.Contact}", href=f"mailto:{self.Contact}", style={
                "font-weight": "normal"
            }),
        ], style={
            "right": "0",
            "bottom": "0",
            "position": "fixed",
            "border-top": "2px solid black",
            "border-left": "2px solid black",
            "margin": "auto auto auto auto",
            "padding": "5px 5px 5px 5px",
        })

        hidden = html.Div(children=[
            dcc.Interval(id=AppAPI.INTERVAL_ID, interval=1000, n_intervals=0, disabled=False),
            dcc.Store(id=AppAPI.SESSION_ID, storage_type="memory"),
            dcc.Location(id=AppAPI.LOCATION_ID, refresh=False)
        ], style={})

        self.App.layout = html.Div(
            id=AppAPI.LAYOUT_ID,
            children=[header, content, footer, hidden],
            style={"font-family": "BNPP Sans"}
        )

    def _init_callbacks(self):

        @self.App.callback(
            dash.Output(AppAPI.SELECTED_ID, "children", allow_duplicate=True),
            dash.Input(AppAPI.LOCATION_ID, "pathname"),
            prevent_initial_call=True)
        def update_description_callback(path: str) -> str | None:
            if not self.Pages: raise PreventUpdate
            endpoint = inspect_file_path(path, header=True)
            return self._page_(endpoint)["description"]

        self.callbacks()

    def link(self, path: str, button: str, description: str, layout):
        module = inspect_file(path).name
        endpoint = inspect_file_path(self.Module / module, header=True)
        order = self._order_()
        dash.register_page(
            module,
            path=path,
            endpoint=endpoint,
            name=button,
            order=order,
            description=description,
            title=self.Title,
            anchor=self.Anchor,
            layout=layout
        )

    def _order_(self):
        order = self._counter_
        self._counter_ += 1
        return order

    def _registry_(self):
        for endpoint, link in dash.page_registry.items():
            if link["anchor"] == self.Anchor and link["title"] == self.Title:
                self._links_[endpoint] = link
        self._links_ = dict(sorted(self._links_.items(), key=lambda item: item[1]["order"]))

    def _page_(self, path: str) -> dict | None:
        return self._links_[path]

    @abstractmethod
    def layout(self):
        raise NotImplementedError

    @abstractmethod
    def callbacks(self):
        raise NotImplementedError

    def run(self):
        return self.App.run_server(port=self.Port, debug=self.Debug)

    def mount(self):
        app = FastAPI()
        app.mount("/", WSGIMiddleware(self.App.server))
        return app
