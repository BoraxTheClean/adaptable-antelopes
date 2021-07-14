import datetime
import os
from asyncio import ensure_future

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.search import start_search
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import MenuContainer, MenuItem, SearchToolbar, TextArea
from pygments.lexers.markup import MarkdownLexer

from application.state import ApplicationState
from constants import NOTES_DIR
from custom_types import MessageDialog, PopUpDialog, ScrollMenuDialog, TextInputDialog


class MenuNav:
    """Menu bar

    Displays menu items

    Handles every action related to menu items

    Handles key bindings for some actions
    """

    def __init__(self):
        """__init__."""
        self.root_container = MenuContainer(
            body=self.body,
            menu_items=[
                MenuItem(
                    "File",
                    children=[
                        MenuItem("New...", handler=self.do_new_file),
                        MenuItem("Open Scroll", handler=self.do_scroll_menu),
                        MenuItem("Save", handler=self.do_save_file),
                        MenuItem("Save as...", handler=self.do_save_as_file),
                        MenuItem("-", disabled=True),
                        MenuItem("Exit", handler=self.do_exit),
                    ],
                ),
                MenuItem(
                    "Edit",
                    children=[
                        MenuItem("Undo", handler=self.do_undo),
                        MenuItem("Cut", handler=self.do_cut),
                        MenuItem("Copy", handler=self.do_copy),
                        MenuItem("Paste", handler=self.do_paste),
                        MenuItem("Delete", handler=self.do_delete),
                        MenuItem("-", disabled=True),
                        MenuItem("Find", handler=self.do_find),
                        MenuItem("Find next", handler=self.do_find_next),
                        # TODO no replace function we can just delete it or try to implement self.do_replace
                        MenuItem("Replace"),
                        MenuItem("Select All", handler=self.do_select_all),
                        MenuItem("Time/Date", handler=self.do_time_date),
                    ],
                ),
                MenuItem(
                    "View",
                    children=[MenuItem("Status Bar", handler=self.do_status_bar)],
                ),
                MenuItem(
                    "Info",
                    children=[
                        MenuItem("About", handler=self.do_about),
                    ],
                ),
            ],
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=16, scroll_offset=1),
                ),
            ],
            key_bindings=self._setup_keybindings(),
        )

    ############ MENU ITEMS #############
    def do_save_file(self) -> None:
        """Try to save. If no file is being edited, save as instead to create a new one."""
        if path := self.application_state.current_path:
            self._save_file_at_path(path, self.text_field.text)
        else:
            self.do_save_as_file()

    def do_save_as_file(self) -> None:
        """Try to Save As a file under a new name/path."""

        async def coroutine() -> None:
            open_dialog = TextInputDialog(
                title="Save As", label_text="Enter the path of the file:"
            )

            path = await self.show_dialog_as_float(open_dialog)
            self.application_state.current_path = path
            if path := self.application_state.current_path:
                self._save_file_at_path(path, self.text_field.text)

        ensure_future(coroutine())

    def do_scroll_menu(self) -> None:
        """Open Scroll Menu"""
        self._show_scroll("Scroll", "buf")

    def do_about(self) -> None:
        """About from menu select"""
        self.show_message("About", "ThoughtBox\nCreated by Adaptable Antelopes.")

    def do_new_file(self) -> None:
        """Makes a new file"""
        self.text_field.text = ""
        self.application_state.current_path = None
        set_title("ThoughtBox - Untitled")

    def do_exit(self) -> None:
        """Exit"""
        get_app().exit()

    def do_time_date(self) -> None:
        """Inserts current datetime into self.text_field from menu"""
        text = datetime.datetime.now().isoformat()
        self.text_field.buffer.insert_text(text)

    def do_undo(self) -> None:
        """Undo"""
        self.text_field.buffer.undo()

    def do_cut(self) -> None:
        """Cut"""
        data = self.text_field.buffer.cut_selection()
        get_app().clipboard.set_data(data)

    def do_copy(self) -> None:
        """Copy"""
        data = self.text_field.buffer.copy_selection()
        get_app().clipboard.set_data(data)

    def do_delete(self) -> None:
        """Delete"""
        self.text_field.buffer.cut_selection()

    def do_find(self) -> None:
        """Find"""
        start_search(self.text_field.control)

    def do_find_next(self) -> None:
        """Fine next"""
        search_state = get_app().current_search_state

        cursor_position = self.text_field.buffer.get_search_position(
            search_state, include_current_position=False
        )
        self.text_field.buffer.cursor_position = cursor_position

    def do_paste(self) -> None:
        """Paste"""
        self.text_field.buffer.paste_clipboard_data(get_app().clipboard.get_data())

    def do_select_all(self) -> None:
        """Select all"""
        self.text_field.buffer.cursor_position = 0
        self.text_field.buffer.start_selection()
        self.text_field.buffer.cursor_position = len(self.text_field.buffer.text)

    def do_status_bar(self) -> None:
        """Opens ar closes status bar"""
        self.application_state.show_status_bar = (
            not self.application_state.show_status_bar
        )

    ############ HANDLERS FOR MENU ITEMS #############
    def _save_file_at_path(self, path: str, text: str) -> None:
        """Saves text (changes) to a file path"""
        try:
            with open(path, "w", encoding="utf8") as f:
                f.write(text)
        except IOError as e:
            self.show_message("Error", "{}".format(e))
        else:
            set_title(f"ThoughtBox - {path}")

    def _show_scroll(self, title: str, text: str) -> None:
        """Shows a MessageDialog with a certain title and text"""

        async def coroutine(self: ThoughtBox) -> None:
            dialog = ScrollMenuDialog(self, title, text)
            await self.show_dialog_as_float(dialog)

        ensure_future(coroutine(self))

    def show_message(self, title: str, text: str) -> None:
        """Shows about message"""

        async def coroutine(self: ThoughtBox) -> None:
            dialog = MessageDialog(title, text)
            await self.show_dialog_as_float(dialog)

        ensure_future(coroutine(self))

    async def show_dialog_as_float(self, dialog: PopUpDialog) -> None:
        """Coroutine what does it return idk? the messageDialogs future result which is None?"""
        float_ = Float(content=dialog)
        # Put given dialog on top of everything
        self.root_container.floats.insert(0, float_)

        app = get_app()

        # Put current window in a temp variable
        focused_before = app.layout.current_window
        # Focus cursor to the given dialog
        app.layout.focus(dialog)
        # Wait for the dialog to finish (returns None)
        result = await dialog.future
        # Re-focus cursor back to window in temp variable
        app.layout.focus(focused_before)

        # Now remove the given dialog
        if float_ in self.root_container.floats:
            self.root_container.floats.remove(float_)

        return result

    def _setup_keybindings(self) -> KeyBindings:
        bindings = KeyBindings()

        @bindings.add("c-k")
        def open_menu(event: KeyPressEvent) -> None:
            """Focus menu with Ctrl-K"""
            event.app.layout.focus(self.root_container.window)

        @bindings.add("escape")
        def close_menu(event: KeyPressEvent) -> None:
            """Focus text field."""
            event.app.layout.focus(self.text_field)

        @bindings.add("c-n")
        def create_new_file(event: KeyPressEvent) -> None:
            """Create new file with Ctrl-N"""
            self.do_new_file()

        @bindings.add("c-s")
        def save_file(event: KeyPressEvent) -> None:
            """Save file with Ctrl-S"""
            self.do_save_file()

        @bindings.add("c-o")
        def open_file(event: KeyPressEvent) -> None:
            """Open file with Ctrl-O"""
            self.do_scroll_menu()

        @bindings.add("c-q")
        def exit_editor(event: KeyPressEvent) -> None:
            """Exit terminal with Ctrl-Q"""
            self.do_exit()

        @bindings.add("c-a")
        def select_all(event: KeyPressEvent) -> None:
            """Select all with Ctrl-A"""
            self.do_select_all()

        @bindings.add("c-x")
        def cut_text(event: KeyPressEvent) -> None:
            """Cut with Ctrl-X"""
            self.do_cut()

        @bindings.add("c-c")
        def copy_text(event: KeyPressEvent) -> None:
            """Copy with Ctrl-C"""
            self.do_copy()

        @bindings.add("c-v")
        def paste_text(event: KeyPressEvent) -> None:
            """Paste with Ctrl-V"""
            self.do_paste()

        @bindings.add("c-z")
        def undo_changes(event: KeyPressEvent) -> None:
            """Undo with Ctrl-Z"""
            self.do_undo()

        return bindings


class ThoughtBox(MenuNav):
    """Thought Box - The minimalist note-taking app"""

    def __init__(self):
        self.application_state = ApplicationState()
        self.search_toolbar = SearchToolbar()
        self.text_field = TextArea(
            lexer=PygmentsLexer(MarkdownLexer),
            scrollbar=True,
            search_field=self.search_toolbar,
        )
        # style of menu can def play around here
        self.style = Style.from_dict(
            {
                "status": "reverse",
                "shadow": "bg:#440044",
            }
        )
        self.body = HSplit(
            [
                self.text_field,
                self.search_toolbar,
                ConditionalContainer(
                    content=VSplit(
                        [
                            # No longer need the bottom title bar
                            # Window(
                            #     FormattedTextControl(get_status_bar_left_text),
                            #     style="class:status",
                            #     align=WindowAlign.LEFT,
                            # ),
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

        self.application = Application(
            layout=self.layout,
            enable_page_navigation_bindings=True,
            style=self.style,
            mouse_support=True,
            full_screen=True,
        )

    def get_statusbar_middle_text(self) -> None:
        """Gets status bar opens menu"""
        return " Press Ctrl-K to open menu. "

    def get_statusbar_right_text(self) -> None:
        """Get status bar for the right text?"""
        return " {}:{}  ".format(
            self.text_field.document.cursor_position_row + 1,
            self.text_field.document.cursor_position_col + 1,
        )

    def run(self) -> None:
        """Run the application"""
        # Create notes directory
        os.makedirs(NOTES_DIR, exist_ok=True)
        self.application.run()
