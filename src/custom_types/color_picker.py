from asyncio import Future

from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer
from prompt_toolkit.layout.containers import VSplit, Container, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label, TextArea, Frame

from custom_types.ui_types import PopUpDialog


class ColorPicker(PopUpDialog):
    """Text Input for the open dialog box"""

    def __init__(
        self, completer: Completer = None
    ):

        self.future = Future()

        def accept_text(buf: Buffer) -> bool:
            """Accepts text"""
            # get_app().layout.focus(ok_button)
            # set style here


            buf.complete_state = None
            return True

        def accept() -> None:
            """Accept"""
            self.future.set_result(self.text_area.text)

        def cancel() -> None:
            """Cancel"""
            self.future.set_result(None)

        self.text_area = TextArea(
            completer=completer,
            multiline=False,
            width=D(preferred=6),
            accept_handler=accept_text,
        )

        self.sample_frame = Button(text="sample text",)

        ok_button = Button(text="OK", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title="Pick A Color",
            body=HSplit([Label(text="Enter a hex:"), self.text_area, self.sample_frame]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
