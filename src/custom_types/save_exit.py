from asyncio import Future

from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label

from constants import DIALOG_WIDTH
from custom_types.ui_types import PopUpDialog


class SaveExitDialog(PopUpDialog):
    """Dialog box to offer option to save and exit, exit without saving, or cancel"""

    def __init__(self, title: str, text: str):
        self.future = Future()

        def set_save_exit() -> None:
            """Save file and exit"""
            self.future.set_result("save")
            
        def set_nosave_exit() -> None:
            """Exit without saving file"""
            self.future.set_result("nosave")

        def set_cancel() -> None:
            """Cancel dialog"""
            self.future.set_result("cancel")

        save_exit_button = Button(text="Yes", handler=set_save_exit)
        nosave_exit_button = Button(text="No", handler=set_nosave_exit)
        cancel_button = Button(text="Cancel", handler = set_cancel)
        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=[save_exit_button, nosave_exit_button, cancel_button],
            width=D(preferred=DIALOG_WIDTH),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
