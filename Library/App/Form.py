from __future__ import annotations

from dash import html, dcc
from typing import TYPE_CHECKING
if TYPE_CHECKING: from Library.App import AppAPI

from Library.App import Component, IconAPI, TextAPI, ButtonAPI, PaginatorAPI, PageAPI

class FormAPI(PageAPI):

    FORM_BACK_INTERNAL_ID: dict
    FORM_BACK_EXTERNAL_ID: dict
    FORM_ACTION_BUTTON_ID: dict
    FORM_NEXT_INTERNAL_ID: dict
    FORM_NEXT_EXTERNAL_ID: dict

    def __init__(self, *,
                 app: AppAPI,
                 path: str,
                 button: str = None,
                 description: str = None,
                 content: Component = None,
                 sidebar: Component = None,
                 navigation: Component = None,
                 add_backward_parent: bool = True,
                 add_backward_children: bool = False,
                 add_current_parent: bool = False,
                 add_current_children: bool = True,
                 add_forward_parent: bool = False,
                 add_forward_children: bool = True,
                 add_back_button: str | bool = False,
                 add_action_button: str = None,
                 add_next_button: str | bool = False) -> None:

        super().__init__(
            app=app,
            path=path,
            button=button,
            description=description,
            content=content,
            sidebar=sidebar,
            navigation=navigation,
            add_backward_parent=add_backward_parent,
            add_backward_children=add_backward_children,
            add_current_parent=add_current_parent,
            add_current_children=add_current_children,
            add_forward_parent=add_forward_parent,
            add_forward_children=add_forward_children
        )

        self._add_back_button_: str | bool = add_back_button
        self._add_action_button_: str = add_action_button
        self._add_next_button_: str | bool = add_next_button

    def _init_ids_(self) -> None:
        self.FORM_ACTION_BUTTON_ID = self.register(type="button", name="action")
        self.FORM_BACK_INTERNAL_ID = self.register(type="button", name="internal-back")
        self.FORM_BACK_EXTERNAL_ID = self.register(type="button", name="external-back")
        self.FORM_NEXT_INTERNAL_ID = self.register(type="button", name="internal-next")
        self.FORM_NEXT_EXTERNAL_ID = self.register(type="button", name="external-next")
        super()._init_ids_()

    def _init_buttons_(self) -> list[Component]:
        buttons = []
        if self._add_back_button_:
            target: str = self._app_.anchorize(path=self._add_back_button_, relative=True) if isinstance(self._add_back_button_, str) else None
            buttons.append(PaginatorAPI(iid=self.FORM_BACK_INTERNAL_ID, eid=self.FORM_BACK_EXTERNAL_ID, label=[
                IconAPI(icon="bi bi-chevron-left"),
                TextAPI(text="  Back")
            ], invert=False, href=target).build())
        if self._add_action_button_:
            buttons.append(ButtonAPI(label=[
                TextAPI(text=self._add_action_button_),
            ], id=self.FORM_ACTION_BUTTON_ID).build())
        if self._add_next_button_:
            target: str = self._app_.anchorize(path=self._add_next_button_, relative=True) if isinstance(self._add_next_button_, str) else None
            buttons.append(PaginatorAPI(iid=self.FORM_NEXT_INTERNAL_ID, eid=self.FORM_NEXT_EXTERNAL_ID, label=[
                TextAPI(text="Next  "),
                IconAPI(icon="bi bi-chevron-right")
            ], invert=True, href=target).build())
        return buttons

    def _init_layout_(self) -> None:
        super()._init_layout_()
        content = [c for c in self._content_ if not isinstance(c, dcc.Store)]
        hidden = [c for c in self._content_ if isinstance(c, dcc.Store)]
        buttons = self._init_buttons_()
        self._log_.debug(lambda: f"Loaded Buttons Layout")
        content = html.Div(children=content, className="form-page-content")
        buttons = html.Div(children=buttons,className="form-page-buttons")
        self._content_ = [content, buttons, hidden]
