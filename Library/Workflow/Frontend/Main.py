from dash import html
import dash_bootstrap_components as dbc

from Library.App import *
from Library.Logging import *
from Library.Workflow.Frontend.Overview import OverviewPageAPI

class WorkflowManagerFrontendAPI(AppAPI):

    def __init__(self):
        super().__init__(
            name="Workflow Manager",
            title="Workflow Manager",
            team="Exotics Trading Team",
            anchor="services/proxy/8090",
            port=8050,
            debug=True
        )

    def pages(self):
        self.link(PageAPI(app=self, path="/", button="Home", description="Home", indexed=True))
        self.link(PageAPI(app=self, path="/dataset", button="Dataset", description="Dataset", indexed=True))
        self.link(PageAPI(app=self, path="/marking", button="Marking", description="Marking", indexed=False))
        self.link(PageAPI(app=self, path="/marking/volatility", button="Volatility", description="Volatility Marking", indexed=True))
        self.link(PageAPI(app=self, path="/marking/forward", button="Forward", description="Forward Marking", indexed=True))
        self.link(PageAPI(app=self, path="/marking/dividends", button="Dividends", description="Dividends Marking", indexed=True))
        self.link(PageAPI(app=self, path="/overlap", button="Overlap", description="Overlap", indexed=True, content=self.overlap()))
        self.link(OverviewPageAPI(app=self))

    def callbacks(self):
        pass

    @staticmethod
    def overlap():
        sections = []

        for i in range(1, 31):  # 30 sections → guaranteed overflow
            sections.append(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4(f"Section {i}"),
                            html.P(
                                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                                * 3
                            ),
                            dbc.Progress(value=(i * 3) % 100, striped=True, animated=True),
                        ]
                    ),
                    className="mb-3",
                )
            )

        return html.Div(
            [
                html.H2("Very Tall Test Page"),
                html.P(
                    "This page is intentionally larger than the available content viewport. "
                    "Only the page area should scroll."
                ),
                html.Hr(),
                *sections,
            ],
            style={
                "padding": "20px",
            },
        )


if __name__ == "__main__":
    log = HandlerLoggingAPI()
    log.web.set_verbose_level(VerboseLevel.Debug)
    log.guard(WorkflowManagerFrontendAPI().run)()
