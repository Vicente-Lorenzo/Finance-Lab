from Library.App import *
from Library.Utility import Component

class OverviewPageAPI(FormAPI):

    def __init__(self, app):
        super().__init__(
            app=app,
            path="/form",
            button="Form",
            description="Form",
            backward="/",
            action="Push",
            forward="/marking"
        )

    def content(self) -> Component:
        #return PaginatorAPI(label="Overview", target=self.app.anchorize("/test")).build()
        return IconButtonAPI(icon="bi bi-question-circle", text="Contacts").build()
