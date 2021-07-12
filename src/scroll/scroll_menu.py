import functools
from asyncio import Future
from os import listdir
from os.path import isdir, isfile, join
from typing import List

from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout import FormattedTextControl, ScrollablePane, Window
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Frame, Label

from constants import CURRENT_WORK_DIR, PADDING_CHAR, PADDING_WIDTH
from custom_types.ui_types import PopUpDialog


class ScrollMenuDialog(PopUpDialog):
    """Scroll menu added to the info tab dialog box"""

    def __init__(self, title: str, text: str, dir: str = CURRENT_WORK_DIR):
        self.future = Future()

        self.body = VSplit(
            children=[
                Label(text="File's content here"),
                Frame(ScrollablePane(HSplit(children=self._get_contents(dir)))),
            ],
            padding_char=PADDING_CHAR,
            padding=PADDING_WIDTH,
        )

        def set_done() -> None:
            """Future object when done return None"""
            self.future.set_result(None)

        # Add chosen file to editor
        ok_button = Button(text="OK", handler=(lambda: set_done()))

        cancel_button = Button(text="Cancel", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=self.body,
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def _get_contents(self, dir: str) -> List[Frame]:
        """Get contents from the given directory

        Args:
            dir (str): directory's name

        Returns:
            List[Frame]: List of frames to add to the container
        """
        frames = [
            Frame(
                Button(
                    text=item,
                    handler=functools.partial(self._display_content, item, dir),
                )
            )
            for item in listdir(dir)
        ]
        # Add a move-up one directory button
        frames.insert(
            0,
            Frame(
                Button(
                    text="../",
                    handler=functools.partial(self._display_content, "..", dir),
                )
            ),
        )
        return frames

    def _display_content(self, target_content: str, target_dir: str) -> None:
        """Display content.

        If target's content is a file, display it in the left column.
        If the target_content is a directory, replace the right column with its content.

        Args:
            target_content (str): Target's content
            target_dir (str): target's directory
        """
        if isfile(join(target_dir, target_content)):
            # open file's content
            with open(join(target_dir, target_content), "r") as f:
                file_content = f.read()
            # Remove any object that isn't HSplit
            self.body.children = list(
                filter(lambda x: type(x) == HSplit, self.body.children)
            )
            # Prepend the file_content to the body
            self.body.children.insert(
                0, Window(content=FormattedTextControl(file_content))
            )
        elif isdir(join(target_dir, target_content)):
            frames = self._get_contents(join(target_dir, target_content))
            # Assuming the last child is the scrolling menu
            self.body.children.pop()
            # Add a new updated menu
            self.body.children.append(
                HSplit(
                    [
                        ScrollablePane(
                            content=HSplit(children=frames), keep_cursor_visible=True
                        )
                    ]
                )
            )
            # Re-focus the cursor back to the dialog
            get_app().layout.focus(self.dialog)
        else:
            raise ValueError("The target' content is neither a file or directory")

    def __pt_container__(self):
        return self.dialog
