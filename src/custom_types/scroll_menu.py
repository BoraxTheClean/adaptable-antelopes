import functools
from asyncio import Future
from os import listdir
from os.path import isdir, isfile, join, realpath, splitext
from typing import List

from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout import FormattedTextControl, ScrollablePane, Window
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.widgets import Button, Dialog, Frame, Label

from constants import NOTES_DIR, PADDING_CHAR, PADDING_WIDTH
from custom_types.ui_types import PopUpDialog


class ScrollMenuDialog(PopUpDialog):
    """Scroll menu added to the info tab dialog box"""

    def __init__(self, commander: object, title: str, text: str, dir: str = NOTES_DIR):
        """Initialize Scroll Menu Dialog

        Args:
            commander (object): Instance of ThoughtBox (required for modifying text in the editor)
            title (str): Title for dialog
            text (str): Body of dialog
            dir (str): Default directory to open
        """
        self.future = Future()
        self.commander = commander
        self.cur_file_path = self.commander.application_state.current_path

        self.body = VSplit(
            children=[
                Label(text="File's content here", dont_extend_height=False),
                Frame(
                    body=ScrollablePane(HSplit(children=self._get_contents(dir))),
                    # style="fg:#ffffff bg:#70ecff bold",
                ),
            ],
            padding_char=PADDING_CHAR,
            padding=PADDING_WIDTH,
        )

        def set_cancel() -> None:
            """Cancel don't open file"""
            self.future.set_result(None)

        # Send error message if attempt to opena ny extension besides .txt and .md
        def set_done() -> None:
            """Handles actions related to adding file's contents to text editor"""
            if self.cur_file_path:
                # The caller is waiting for self.future so setting it to None will
                # be a flag to indicate that we're done with this dialog
                self.future.set_result(None)
                # Only add to text_editor if the given file is text file or markdown file.
                if splitext(self.cur_file_path)[1] in (".txt", ".md"):
                    self.commander.application_state.current_path = self.cur_file_path
                    with open(self.cur_file_path, "r") as f:
                        f_content = f.read()

                    self.commander.current_path = self.cur_file_path
                    self.commander.text_field.text = f_content

                else:
                    # Else show a popup message revealing the error message
                    self.commander.show_message(
                        title="extension_error",
                        text="Unsupported file extension. Only '.txt' and '.md' are supported",
                    )
            set_title(f"ThoughtBox - {self.cur_file_path}")

        # Add chosen file to editor
        self.ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.cancel_button = Button(text="Cancel", handler=(lambda: set_cancel()))

        self.dialog = Dialog(
            title=title,
            body=self.body,
            buttons=[self.ok_button, self.cancel_button],
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
        # Add a move-up one directory button, except if in NOTES_DIR
        if realpath(dir).split("/")[-1] != NOTES_DIR:
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
                # Read up to 1000th character.
                file_content = f.read(1000)
            self.cur_file_path = join(target_dir, target_content)

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
            get_app().layout.focus(self.body)
        else:
            raise ValueError("The target' content is neither a file or directory")

    def __pt_container__(self):
        return self.dialog
