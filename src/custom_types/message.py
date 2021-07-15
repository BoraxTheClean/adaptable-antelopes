from asyncio import Future

from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label

from constants import DIALOG_WIDTH
from custom_types.ui_types import PopUpDialog


class MessageDialog(PopUpDialog):
    """About tab dialog box"""

    def __init__(self, title: str, text: str):
        self.future = Future()

        def set_done() -> None:
            """Close this dialog by returning None to indicate the caller that it's done."""
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=D(preferred=DIALOG_WIDTH),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
