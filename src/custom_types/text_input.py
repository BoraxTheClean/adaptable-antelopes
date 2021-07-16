from asyncio import Future

from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label, TextArea

from constants import DIALOG_WIDTH
from custom_types.ui_types import PopUpDialog


class TextInputDialog(PopUpDialog):
    """Text Input for the open dialog box"""

    def __init__(
        self,
        title: str = "",
        label_text: str = "",
        completer: Completer = None,
    ):
        self.future = Future()

        def accept_text(buf: Buffer) -> bool:
            """Accepts text"""
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept() -> None:
            """Accept and returns the input"""
            self.future.set_result(self.text_area.text)

        def cancel() -> None:
            """Cancel to close out the dialog"""
            self.future.set_result(None)

        self.text_area = TextArea(
            completer=completer,
            multiline=False,
            width=D(preferred=40),
            accept_handler=accept_text,
        )

        ok_button = Button(text="OK", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=DIALOG_WIDTH),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
