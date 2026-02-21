from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: from Library.App import AppAPI
from Library.App.Page import PageAPI
from Library.App.Component import Component, IconAPI, TextAPI, ButtonAPI, PaginatorAPI, ContainerAPI


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
                 add_next_button: str | bool = False,
                 back_button_label: str = "Back",
                 next_button_label: str = "Next") -> None:

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
        self._back_button_label_: str = back_button_label
        self._next_button_label_: str = next_button_label

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
            target: str = self.app.endpointize(path=self._add_back_button_, relative=True) if isinstance(self._add_back_button_, str) else None
            buttons.append(PaginatorAPI(
                iid=self.FORM_BACK_INTERNAL_ID,
                eid=self.FORM_BACK_EXTERNAL_ID,
                label=[IconAPI(icon="bi bi-chevron-left"), TextAPI(text=f"  {self._back_button_label_}")],
                invert=False,
                href=target,
                background="white",
                outline_color="black",
                outline_style="solid",
                outline_width="1px",
                stylename="form-page-button"
            ))
        if self._add_action_button_:
            buttons.append(ButtonAPI(
                id=self.FORM_ACTION_BUTTON_ID,
                label=[TextAPI(text=self._add_action_button_)],
                background="white",
                outline_color="black",
                outline_style="solid",
                outline_width="1px",
                stylename="form-page-button"
            ))
        if self._add_next_button_:
            target: str = self.app.endpointize(path=self._add_next_button_, relative=True) if isinstance(self._add_next_button_, str) else None
            buttons.append(PaginatorAPI(
                iid=self.FORM_NEXT_INTERNAL_ID,
                eid=self.FORM_NEXT_EXTERNAL_ID,
                label=[TextAPI(text="Next  "), IconAPI(icon="bi bi-chevron-right")],
                invert=True,
                href=target,
                background="white",
                outline_color="black",
                outline_style="solid",
                outline_width="1px",
                stylename="form-page-button"
            ))
        return self.normalize([*buttons])

    def _init_content_(self) -> list[Component]:
        hidden = self._init_hidden_()
        self._log_.debug(lambda: f"Loaded Hidden Layout")
        buttons = self._init_buttons_()
        buttons = ContainerAPI(element=buttons, stylename="form-page-buttons").build()
        self._log_.debug(lambda: f"Loaded Buttons Layout")
        content = self.normalize(self._content_ or self.content())
        content = ContainerAPI(element=content, stylename="form-page-content").build()
        return self.normalize([*content, *buttons, *hidden])
