from Library.Utility import PathAPI, htmlize, format

class ReportAPI:

    def __init__(self, data: str | PathAPI, **kwargs):
        from dash import html
        report = data.file.read_text() if isinstance(data, PathAPI) else data
        self._report_ = htmlize([html.Br() if not line else html.Div(children=line, **kwargs) for line in report.split("\n")])

    def __call__(self, **kwargs):
        return format(self._report_, **kwargs)

    def __repr__(self) -> str:
        return repr(self._report_)
