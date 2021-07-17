import os
import os.path
from shutil import copyfile

from prompt_toolkit.application import Application
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea
from pygments.lexers.markup import MarkdownLexer

from application.state import ApplicationState
from constants import ASSETS_DIR, NOTES_DIR, WELCOME_PAGE
from navigation.menu_bar import MenuNav
from utils import display_path


class ThoughtBox(MenuNav):
    """Thought Box - The minimalist note-taking app"""

    def __init__(self):
        # Create internal application directory.
        os.makedirs(NOTES_DIR, exist_ok=True)
        # If welcome page isn't present, create it.
        if not os.path.isfile(os.path.join(NOTES_DIR, WELCOME_PAGE)):
            copyfile(
                os.path.join(ASSETS_DIR, WELCOME_PAGE),
                os.path.join(NOTES_DIR, WELCOME_PAGE),
            )

        self.application_state = ApplicationState()

        self.search_toolbar = SearchToolbar()
        # Define the area where users enter text.
        self.text_field = TextArea(
            lexer=PygmentsLexer(MarkdownLexer),
            scrollbar=True,
            search_field=self.search_toolbar,
        )
        # If the application state has a path saved, we open the file to that path on boot up.
        # If saved path is invalid, open a new file.
        if self.application_state.current_path:
            try:
                with open(self.application_state.current_path, "r") as f:
                    self.text_field.text = f.read()
            except IOError:
                self.application_state.current_path = None

        self.style = Style.from_dict(
            {
                "frame-label": "bg:#ffffff #000000",
                "status": "reverse",
                "shadow": "bg:#000000 #ffffff",
                "menu": "bg:#004444",
                "menu-bar": "bg:#00ff00",
                "dialog.body": "bg:#111111 #00aa44",
            }
        )
        # Define the UI elements to appear on the screen.
        # 1. The text field where users write and read notes.
        # 2. Menu tool bar
        # 3. An optional status bar at the bottom of the page.
        self.body = HSplit(
            [
                self.text_field,
                self.search_toolbar,
                ConditionalContainer(
                    content=VSplit(
                        [
                            Window(
                                FormattedTextControl(self.get_statusbar_middle_text),
                                style="class:status",
                            ),
                            Window(
                                FormattedTextControl(self.get_statusbar_right_text),
                                style="class:status.right",
                                width=9,
                                align=WindowAlign.RIGHT,
                            ),
                        ],
                        height=1,
                    ),
                    filter=Condition(lambda: self.application_state.show_status_bar),
                ),
            ]
        )
        # Initialize super class to get self.root_container
        super().__init__()

        self.layout = Layout(self.root_container, focused_element=self.text_field)

        # Main application here
        self.application = Application(
            layout=self.layout,
            enable_page_navigation_bindings=True,
            style=self.style,
            mouse_support=True,
            full_screen=True,
            after_render=self.set_title_bar,
        )

    def get_statusbar_middle_text(self) -> None:
        """Display a shortcut for opening the menu in the status bar."""
        return " Press Ctrl-K to open menu. "

    def get_statusbar_right_text(self) -> None:
        """Display the current position of the cursor."""
        return " {}:{}  ".format(
            self.text_field.document.cursor_position_row + 1,
            self.text_field.document.cursor_position_col + 1,
        )

    def set_title_bar(self, app: Application) -> None:
        """Set the title bar to the current file as soon as the app starts"""
        if path := self.application_state.current_path:
            set_title(f"ThoughtBox - {display_path(path)}")
        else:
            set_title("ThoughtBox - Untitled")

    def run(self) -> None:
        """Run the application"""
        self.application.run()
