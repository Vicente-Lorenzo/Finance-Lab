from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: from Library.App import AppAPI
from Library.App.Page import PageAPI
from Library.App.Callback import ComponentID
from Library.App.Component import Component, IconAPI, TextAPI, ButtonAPI, PaginatorAPI, ContainerAPI

class FormAPI(PageAPI):

    FORM_BACK_INTERNAL_ID: ComponentID | dict = ComponentID()
    FORM_BACK_EXTERNAL_ID: ComponentID | dict = ComponentID()
    FORM_ACTION_BUTTON_ID: ComponentID | dict = ComponentID()
    FORM_NEXT_INTERNAL_ID: ComponentID | dict = ComponentID()
    FORM_NEXT_EXTERNAL_ID: ComponentID | dict = ComponentID()

    def __init__(self, *,
                 app: AppAPI,
                 path: str,
                 anchor: str = None,
                 endpoint: str = None,
                 redirect: str = None,
                 button: str = None,
                 description: str = None,
                 content: Component | list[Component] = None,
                 sidebar: Component | list[Component] = None,
                 navigation: Component | list[Component] = None,
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
            anchor=anchor,
            endpoint=endpoint,
            redirect=redirect,
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

    def __init_ids__(self) -> None:
        self.FORM_ACTION_BUTTON_ID: dict = self.register(type="button", name="action")
        self.FORM_BACK_INTERNAL_ID: dict = self.register(type="button", name="internal-back")
        self.FORM_BACK_EXTERNAL_ID: dict = self.register(type="button", name="external-back")
        self.FORM_NEXT_INTERNAL_ID: dict = self.register(type="button", name="internal-next")
        self.FORM_NEXT_EXTERNAL_ID: dict = self.register(type="button", name="external-next")
        super().__init_ids__()

    def __init_button_layout__(self) -> list[Component]:
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
                stylename="button"
            ))
        if self._add_action_button_:
            buttons.append(ButtonAPI(
                id=self.FORM_ACTION_BUTTON_ID,
                label=[TextAPI(text=self._add_action_button_)],
                background="white",
                outline_color="black",
                outline_style="solid",
                outline_width="1px",
                stylename="button"
            ))
        if self._add_next_button_:
            target: str = self.app.endpointize(path=self._add_next_button_, relative=True) if isinstance(self._add_next_button_, str) else None
            buttons.append(PaginatorAPI(
                iid=self.FORM_NEXT_INTERNAL_ID,
                eid=self.FORM_NEXT_EXTERNAL_ID,
                label=[TextAPI(text=f"{self._next_button_label_}  "), IconAPI(icon="bi bi-chevron-right")],
                invert=True,
                href=target,
                background="white",
                outline_color="black",
                outline_style="solid",
                outline_width="1px",
                stylename="button"
            ))
        return self.normalize([*buttons])

    def __init_content_layout__(self) -> list[Component]:
        hidden = self.__init_hidden_layout__()
        self._log_.debug(lambda: f"Loaded Hidden Layout")
        buttons = self.__init_button_layout__()
        buttons = ContainerAPI(elements=buttons, classname="controls").build()
        self._log_.debug(lambda: f"Loaded Buttons Layout")
        content = self.normalize(self._content_ or self.content())
        form = ContainerAPI(elements=[*content, *buttons], classname="form").build()
        return self.normalize([*form, *hidden])

    def __init_sidebar_layout__(self) -> list[Component]:
        sidebar = self.normalize(self._sidebar_ or self.sidebar())
        form = ContainerAPI(elements=[*sidebar], classname="form").build()
        return self.normalize([*form])