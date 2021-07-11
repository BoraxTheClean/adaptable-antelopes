from asyncio import Future
from types.ui_types import PopUpDialog

from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Frame, Label, TextArea


class ScrollMenuDialog(PopUpDialog):
    """Scroll menu added to the info tab dialog box"""

    def __init__(self, title: str, text: str):
        self.future = Future()

        def set_done() -> None:
            """Future object when done return None"""
            self.future.set_result(None)

        # changed text from OK to see where this is
        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit(
                [
                    Label("ScrollContainer Demo"),
                    Frame(
                        ScrollablePane(
                            HSplit(
                                [
                                    Frame(
                                        TextArea(
                                            text=f"label-{i}",
                                            # completer=animal_completer,
                                        )
                                    )
                                    for i in range(20)
                                ]
                            )
                        ),
                    ),
                ]
            ),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
