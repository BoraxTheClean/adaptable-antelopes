from asyncio import Future

from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label

from constants import DIALOG_WIDTH
from custom_types.ui_types import PopUpDialog
from utils import display_path


class ConfirmDialog(PopUpDialog):
    """Dialog box to confirm or cancel"""

    def __init__(self, title: str, text: str):
        self.future = Future()

        def set_done() -> None:
            """Confirm the dialog."""
            self.future.set_result(True)

        def set_cancel() -> None:
            """Cancel the dialog."""
            self.future.set_result(False)

        yes_button = Button(text="Yes", handler=set_done)
        no_button = Button(text="No", handler=set_cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=display_path(text))]),
            buttons=[yes_button, no_button],
            width=D(preferred=DIALOG_WIDTH),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
