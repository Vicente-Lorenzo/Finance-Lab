from __future__ import annotations

from dash import html
from typing import TYPE_CHECKING
if TYPE_CHECKING: from Library.App import AppAPI

from Library.App import IconAPI, TextAPI, ButtonAPI, PaginatorAPI, PageAPI
from Library.Utility import Component

class FormAPI(PageAPI):

    ACTION_BUTTON_ID: dict = None

    def __init__(
        self,
        app: AppAPI,
        path: str,
        button: str = None,
        description: str = None,
        indexed: bool = True,
        content: Component = None,
        sidebar: Component = None,
        navigation: Component = None,
        backward: str = None,
        forward: str = None,
        action: str = None):

        super().__init__(
            app=app,
            path=path,
            button=button,
            description=description,
            indexed=indexed,
            content=content,
            sidebar=sidebar,
            navigation=navigation,
        )

        self.backward: str = backward
        self.forward: str = forward
        self.action: str = action

    def _init_ids_(self) -> None:
        super()._init_ids_()
        if self.action: self.ACTION_BUTTON_ID = self.identify(type="button", name="action")

    def form(self) -> Component | list[Component]:
        return super().content()

    def content(self) -> Component | list[Component]:
        buttons = []
        if self.backward: buttons.append(PaginatorAPI(label=[
            IconAPI(icon="bi bi-chevron-left"),
            TextAPI(text="  Back")
        ], invert=False, target=self.app.anchorize(self.backward)).build())
        if self.action: buttons.append(ButtonAPI(label=[
            TextAPI(text=self.action),
        ], key=self.ACTION_BUTTON_ID).build())
        if self.forward: buttons.append(PaginatorAPI(label=[
            TextAPI(text="Next  "),
            IconAPI(icon="bi bi-chevron-right")
        ], invert=True, target=self.app.anchorize(self.forward)).build())

        form = html.Div(self.form(), className="form-page-content")
        buttons = html.Div(buttons,className="form-page-buttons")
        return [form, buttons]
