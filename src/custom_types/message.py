from asyncio import Future

from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label

from custom_types.ui_types import PopUpDialog


class MessageDialog(PopUpDialog):
    """About tab dialog box"""

    def __init__(self, title: str, text: str):
        self.future = Future()

        def set_done() -> None:
            """Future object when done return None"""
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
