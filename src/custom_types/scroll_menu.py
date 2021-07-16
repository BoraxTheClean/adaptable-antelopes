import functools
from asyncio import Future
from os import listdir
from os.path import basename, dirname, isdir, isfile, join, realpath
from typing import List

from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout import FormattedTextControl, ScrollablePane, Window
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Frame, Label

# from application.editor import ThoughtBox
from constants import NOTES_DIR, PADDING_CHAR, PADDING_WIDTH
from custom_types.ui_types import PopUpDialog


class ScrollMenuDialog(PopUpDialog):
    """Scroll menu added to the info tab dialog box"""

    def __init__(
        self, title: str, text: str, directory: str = NOTES_DIR, show_files: bool = True
    ):
        """Initialize Scroll Menu Dialog

        Args:
            title (str): Title for dialog
            text (str): Body of dialog
            directory (str): Default directory to open
            show_files (bool): Whether or not to show files in the scroll menu
        """
        self.future = Future()
        self.path = None if show_files else directory

        user_displayed_directory = (
            "Your Thought Box" if directory == NOTES_DIR else directory
        )

        self.body = VSplit(
            children=[
                Label(text=text, dont_extend_height=False),
                Frame(
                    title=user_displayed_directory,
                    body=ScrollablePane(
                        HSplit(
                            children=self._get_contents(
                                directory, show_files=show_files
                            )
                        )
                    ),
                    # style="fg:#ffffff bg:#70ecff bold",
                ),
            ],
            padding_char=PADDING_CHAR,
            padding=PADDING_WIDTH,
        )

        def set_cancel() -> None:
            """Cancel don't open file"""
            self.future.set_result(None)

        # Send error message if attempt to open any extension besides .txt and .md
        def set_done() -> None:
            """Handles actions related to adding file's contents to text editor"""
            self.future.set_result(self.path)

        # Add chosen file to editor
        self.ok_button = Button(text="OK", handler=set_done)

        self.cancel_button = Button(text="Cancel", handler=set_cancel)

        self.dialog = Dialog(
            title=title,
            body=self.body,
            buttons=[self.ok_button, self.cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def _get_contents(self, directory: str, show_files: bool = True) -> List[Frame]:
        """Get file names and content previews from the given directory.

        Args:
            directory (str): directory's name
            show_files (bool): Whether or not to show files in the scroll menu

        Returns:
            List[Frame]: List of frames to add to the container
        """
        frames = []
        for file_name in listdir(directory):
            # Make sure that the file:
            # 1. Does not start with "."
            # 2a. If show_files, make sure it ends with '.txt' or '.md'
            # 2b. Otherwise, make sure it's a folder
            if not file_name.startswith(".") and (
                (
                    show_files
                    and (file_name.endswith(".txt") or file_name.endswith(".md"))
                )
                or isdir(join(directory, file_name))
            ):
                frames.append(
                    Frame(
                        Button(
                            text=file_name,
                            handler=functools.partial(
                                self._display_content, file_name, directory, show_files
                            ),
                        )
                    )
                )

        # Add a move-up one directory button, except if in NOTES_DIR
        if basename(realpath(directory)) != NOTES_DIR:
            frames.insert(
                0,
                Frame(
                    Button(
                        text="../",
                        handler=functools.partial(
                            self._display_content, "..", directory, show_files
                        ),
                    )
                ),
            )
        return frames

    def _display_content(
        self, target_content: str, target_dir: str, show_files: bool = True
    ) -> None:
        """Display content.

        If target's content is a file, display it in the left column.
        If the target_content is a directory, replace the right column with its content.

        Args:
            target_content (str): Target's content
            target_dir (str): target's directory
            show_files (bool): Whether or not to show files in the scroll menu
        """
        self.path = join(target_dir, target_content)
        if isfile(self.path):
            # open file's content
            with open(join(target_dir, target_content), "r") as f:
                # Read up to 1000th character.
                file_content = f.read(1000)
            self.path = join(target_dir, target_content)

            # Remove any object that isn't HSplit
            self.body.children = list(
                filter(lambda x: type(x) == HSplit, self.body.children)
            )
            # Prepend the file_content to the body
            self.body.children.insert(
                0, Window(content=FormattedTextControl(file_content))
            )
            # Re-focus cursor to ok_button
            get_app().layout.focus(self.ok_button)
        elif isdir(self.path):
            if target_content == "..":
                self.path = dirname(target_dir)
            frames = self._get_contents(self.path, show_files=show_files)
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
            get_app().layout.focus(self.body)
        else:
            raise ValueError("The target content is neither a file nor directory")

    def __pt_container__(self):
        return self.dialog
