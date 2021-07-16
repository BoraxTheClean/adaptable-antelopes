import functools
import string
from asyncio import Future
import json
from typing import List

from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import VSplit, Container, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Button, Dialog, Label, TextArea, Frame

from custom_types.ui_types import PopUpDialog
from constants import USER_SETTINGS_DIR




class ColorPicker(PopUpDialog):
    """Text Input for the open dialog box"""

    def __init__(
            self, completer: Completer = None
    ):
        self.future = Future()

        def is_hex(s):
            """Validate that the user entered path is
            1. len(6)
            2. only contains 0-9 and a-f"""
            if len(s) == 6:
                hex_digits = set(string.hexdigits)
                # if s is long, then it is faster to check against a set
                return all(c in hex_digits for c in s)
            else:
                return False

        def prev() -> None:
            if is_hex(self.text_area.text):

                get_app().style = Style.from_dict(
                    {
                        "menu-bar": f"bg:#{self.text_area.text}",
                    }
                )
                self.promp_label.text = 'Enter a hex:'
            else:
                self.promp_label.text = 'Invalid Hex'


        def accept_text(buf: Buffer) -> bool:
            prev()
            buf.complete_state = None
            return True

        def accept() -> bool:
            """Accept"""
            if is_hex(self.text_area.text):
                # save to user settings
                with open(USER_SETTINGS_DIR, 'r') as user_file:
                    user_json = user_file.read()
                    user_settings = json.loads(user_json)
                    user_settings['style']['menu-bar'] = f"bg:#{self.text_area.text}"
                with open(USER_SETTINGS_DIR,'w') as user_file:
                    user_file.write(json.dumps(user_settings))

                self.future.set_result(False)
            else:
                # invalid hex don't set_future
                self.promp_label.text = 'Invalid Hex'


        def cancel() -> bool:
            """Cancel"""
            self.future.set_result(True)

        self.text_area = TextArea(
            completer=completer,
            multiline=False,
            width=D(preferred=6),
            accept_handler=accept_text,
        )

        self.promp_label = Label(text="Enter a hex:")

        preview_button = Button('Preview', handler=prev)
        ok_button = Button(text="Apply", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title="Pick A Color",
            body=HSplit([self.promp_label, self.text_area]),
            buttons=[preview_button, ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog




'''
class ScrollMenuColorDialog(PopUpDialog):
    """Scroll menu added to the info tab dialog box
    {
    "frame-label": "bg:#ffffff #000000",
    "status": "reverse",
    "shadow": "bg:#000000 #ffffff",
    "menu": "bg:#004400",
    "menu-bar": "bg:#00ff00",
    "dialog.body": "bg:#111111 #00aa44",}"""

    def __init__(self, commander: object):
        """Initialize Scroll Menu Dialog

        Args:
            commander (object): Instance of ThoughtBox (required for modifying text in the editor)
        """
        self.future = Future()
        self.commander = commander

        # self.cur_style = self.commander.application_state.cur_style

        style_list = ['frame-label', 'menu', 'menu-bar', 'dialog.body']

        self.body = VSplit(
            padding_char=PADDING_CHAR,
            children=[
                Label(text="Style Elements", dont_extend_height=False),
                Frame(body=ScrollablePane(HSplit(children=self._get_contents(style_list))))
            ],
            padding=PADDING_WIDTH,
        )

        def set_cancel() -> None:
            """Cancel don't open file"""
            self.future.set_result(None)

        # Send error message if attempt to open any extension besides .txt and .md
        def set_done() -> None:
            """Handles actions related to adding file's contents to text editor"""
            if self.cur_style:
                # The caller is waiting for self.future so setting it to None will
                # be a flag to indicate that we're done with this dialog
                self.future.set_result(None)
                self.commander.show_message(
                    title="extension_error",
                    text="Unsupported file extension. Only '.txt' and '.md' are supported",
                )

        # Add chosen file to editor
        self.ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.cancel_button = Button(text="Cancel", handler=(lambda: set_cancel()))

        self.dialog = Dialog(
            title='Color Picker',
            body=self.body,
            buttons=[self.ok_button, self.cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def _get_contents(self, opt_list=None) -> List[Frame]:
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
                    handler=functools.partial(self._display_content, item),
                )
            )
            for item in opt_list
        ]

        # Add a move-up one a level if your in an element
        if self.level == 1:
            frames.insert(
                0,
                Frame(
                    Button(
                        text="../",
                        handler=functools.partial(self._display_content, ".."),
                    )
                ),
            )
        return frames

    def _display_content(self, target_content: str) -> None:
        """Display content.

        If target's content is a file, display it in the left column.
        If the target_content is a directory, replace the right column with its content.

        Args:
            target_content (str): Target's content
            target_dir (str): target's directory
        """
        # on he first level with men. menu-bar ...
        if self.level == 0:
            frames = self._get_contents(['bg','fg'])

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
            frames = self._get_contents()
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
'''
