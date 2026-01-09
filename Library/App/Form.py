from __future__ import annotations

from dash import html
from typing import TYPE_CHECKING
if TYPE_CHECKING: from Library.App import AppAPI

from Library.App import IconAPI, TextAPI, ButtonAPI, PaginatorAPI, PageAPI
from Library.Utility import Component

class FormAPI(PageAPI):

    ACTION_BUTTON_ID: dict = None
    BACKWARD_INTERNAL_ID: dict = None
    BACKWARD_EXTERNAL_ID: dict = None
    FORWARD_INTERNAL_ID: dict = None
    FORWARD_EXTERNAL_ID: dict = None

    def __init__(self, *,
                 app: AppAPI,
                 path: str,
                 button: str = None,
                 description: str = None,
                 indexed: bool = True,
                 content: Component = None,
                 sidebar: Component = None,
                 navigation: Component = None,
                 backward: str | bool = False,
                 forward: str | bool = False,
                 action: str = None) -> None:

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

        self.backward: str | bool = backward
        self.forward: str | bool = forward
        self.action: str = action

    def _init_ids_(self) -> None:
        self.ACTION_BUTTON_ID = self.register(type="button", name="action")
        self.BACKWARD_INTERNAL_ID = self.register(type="button", name="internal-backward")
        self.BACKWARD_EXTERNAL_ID = self.register(type="button", name="external-backward")
        self.FORWARD_INTERNAL_ID = self.register(type="button", name="internal-forward")
        self.FORWARD_EXTERNAL_ID = self.register(type="button", name="external-forward")
        super()._init_ids_()

    def _init_buttons_(self) -> Component | list[Component]:
        buttons = []
        if self.backward:
            target: str = self.app.anchorize(path=self.backward, relative=True) if isinstance(self.backward, str) else None
            buttons.append(PaginatorAPI(iid=self.BACKWARD_INTERNAL_ID, eid=self.BACKWARD_EXTERNAL_ID, label=[
                IconAPI(icon="bi bi-chevron-left"),
                TextAPI(text="  Back")
            ], invert=False, href=target).build())
        if self.action:
            buttons.append(ButtonAPI(label=[
                TextAPI(text=self.action),
            ], id=self.ACTION_BUTTON_ID).build())
        if self.forward:
            target: str = self.app.anchorize(path=self.forward, relative=True) if isinstance(self.forward, str) else None
            buttons.append(PaginatorAPI(iid=self.FORWARD_INTERNAL_ID, eid=self.FORWARD_EXTERNAL_ID, label=[
                TextAPI(text="Next  "),
                IconAPI(icon="bi bi-chevron-right")
            ], invert=True, href=target).build())
        return buttons

    def _init_layout_(self) -> None:
        super()._init_layout_()
        *content, hidden = self._content_
        buttons = self._init_buttons_()
        self._log_.debug(lambda: f"Loaded Buttons Layout")
        content = html.Div(*content, className="form-page-content")
        buttons = html.Div(buttons,className="form-page-buttons")
        self._content_ = [content, buttons, hidden]
