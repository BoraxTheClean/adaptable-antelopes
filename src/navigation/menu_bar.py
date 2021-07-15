import datetime
import json
import os
from asyncio import ensure_future
from typing import Optional, Union

from emoji import emojize
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import Float
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.search import start_search
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.widgets import MenuContainer, MenuItem

from constants import DIALOG_WIDTH, NOTES_DIR
from custom_types import (
    ConfirmDialog,
    MessageDialog,
    PopUpDialog,
    ScrollMenuDialog,
    TextInputDialog,
)


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
                        MenuItem("New Note...", handler=self.do_new_file),
                        MenuItem("Open", handler=self.do_scroll_menu),
                        MenuItem("Save", handler=self.do_save_file),
                        MenuItem("Save as...", handler=self.do_save_as_file),
                        MenuItem("-", disabled=True),
                        MenuItem("New Folder", handler=self.do_new_folder),
                        MenuItem("Rename Folder", handler=self.do_rename_folder),
                        MenuItem("Delete Folder", handler=self.do_delete_folder),
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
                        MenuItem("Text To Emoji", handler=self.do_convert_to_emoji),
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

    #
    # def do_save_as_file(self) -> None:
    #     """Try to Save As a file under a new name/path."""
    #
    #     async def coroutine() -> None:
    #         open_dialog = TextInputDialog(
    #             title="Save As", label_text="Enter the path of the file:"
    #         )
    #
    #         path = await self.show_dialog_as_float(open_dialog)
    #         self.application_state.current_path = path
    #         if path := self.application_state.current_path:
    #             self._save_file_at_path(path, self.text_field.text)
    #
    #     ensure_future(coroutine())

    def do_save_file(self) -> None:
        """Try to save. If no file is being edited, save as instead to create a new one."""
        if path := self.application_state.current_path:
            self._save_file_at_path(path, self.text_field.text)
        else:
            self.do_save_as_file()

    def do_save_as_file(self) -> None:
        """Try to Save As a file under a new name/path."""

        async def coroutine() -> None:
            """
            Prompt the user for a file path to save their note.

            If the path entered is a valid file name, save the current note at that path.
            """
            open_dialog = TextInputDialog(
                title="Save As", label_text="Enter the path of the file:"
            )
            user_entered_path = await self.show_dialog_as_float(open_dialog)
            if user_entered_path is None:
                return

            dir_name, file_name = os.path.split(user_entered_path)
            # Validate that the user entered path:
            # 1. Is not the empty string or None
            # 2. Doesn't consist exclusively of whitespace
            # 3. Doesn't start with "."
            # 4. Contains either an existing directory or the empty string
            if (
                user_entered_path
                and not user_entered_path.isspace()
                and not user_entered_path.startswith(".")
                and not file_name.startswith(".")
                and (
                    dir_name == "" or os.path.exists(os.path.join(NOTES_DIR, dir_name))
                )
            ):
                if not (
                    user_entered_path.endswith(".txt")
                    or user_entered_path.endswith(".md")
                ):
                    user_entered_path += ".txt"
                path = os.path.join(NOTES_DIR, user_entered_path)

                if os.path.isfile(path):
                    open_dialog = ConfirmDialog(
                        title="Save As",
                        text=f"The file {user_entered_path} already exists. Do you want to overwrite it?",
                    )
                    override = await self.show_dialog_as_float(open_dialog)
                    if not override:
                        return

                path = os.path.join(NOTES_DIR, user_entered_path)
                self._save_file_at_path(path, self.text_field.text)
            else:
                self.show_message("Invalid Path", "Please enter a valid file name.")

        ensure_future(coroutine())

    def do_scroll_menu(self) -> None:
        """Open Scroll Menu"""

        async def coroutine(self: MenuNav) -> None:
            dialog = ScrollMenuDialog(
                title="Open Note",
                text="File content here",
                directory=self.application_state.current_dir,
                show_files=True,
            )
            path = await self.show_dialog_as_float(dialog)
            # Only add to text_editor if the given file is text file or markdown file.
            if path:
                if os.path.splitext(path)[1] in (".txt", ".md"):
                    self.application_state.current_path = path
                    with open(path, "r") as f:
                        self.text_field.text = f.read()

                    set_title(f"ThoughtBox - {path}")
                else:
                    # Else show a popup message revealing the error message
                    self.show_message(
                        title="extension_error",
                        text="Unsupported file extension. Only '.txt' and '.md' are supported",
                    )

        ensure_future(coroutine(self))

    def do_about(self) -> None:
        """About from menu select"""
        self.show_message("About", "ThoughtBox\nCreated by Adaptable Antelopes.")

    def do_new_file(self) -> None:
        """Makes a new file"""
        self.text_field.text = ""
        self.application_state.current_path = None
        set_title("ThoughtBox - Untitled")

    def do_new_folder(self) -> None:
        """Creates a folder"""

        async def coroutine(self: MenuNav) -> None:
            dialog = ScrollMenuDialog(
                title="New Folder",
                text="Choose the location of the new folder.",
                directory=self.application_state.current_dir,
                show_files=False,
            )
            path = await self.show_dialog_as_float(dialog)
            if not path:
                return

            dialog = TextInputDialog(
                "New Folder", label_text="Enter the name of the folder:"
            )
            folder_name = await self.show_dialog_as_float(dialog)
            if folder_name is None:
                return

            # Validate that the folder name:
            # 1. Is not the empty string or None
            # 2. Doesn't consist exclusively of whitespace
            # 3. Doesn't start with "."
            if (
                folder_name
                and not folder_name.isspace()
                and not folder_name.startswith(".")
            ):
                if os.path.exists(os.path.join(path, folder_name)):
                    return self.show_message(
                        title="New Folder", text="That folder already exists."
                    )

                try:
                    os.mkdir(os.path.join(path, folder_name))
                except OSError:
                    self.show_message(
                        title="New Folder",
                        text="Please enter a valid folder name.",
                    )
                else:
                    self.show_message(
                        title="New Folder",
                        text=f"Folder at {os.path.join(path, folder_name)} was created.",
                    )
            else:
                self.show_message(
                    title="New Folder",
                    text="Please enter a valid folder name.",
                )

        ensure_future(coroutine(self))

    def do_rename_folder(self) -> None:
        """Renames a folder"""

    def do_delete_folder(self) -> None:
        """Delete a folder"""

    def do_exit(self) -> None:
        """Exit"""
        settings_path = os.path.join(NOTES_DIR, ".user_setting.json")
        with open(settings_path, "r") as f:
            user = json.load(f)

        self.application_state.user_settings[
            "last_path"
        ] = self.application_state.current_path
        user["last_path"] = self.application_state.current_path
        with open(settings_path, "w") as f:
            json.dump(user, f)
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

    def do_convert_to_emoji(self) -> None:
        """Convert all ascii emoji to unicode emoji"""
        # save cursor position
        c_pos = (
            self.text_field.document.cursor_position_row,
            self.text_field.document.cursor_position_col,
        )
        self.text_field.text = emojize(
            self.text_field.text, use_aliases=True, variant="emoji_type"
        )
        # Move cursor back to saved position
        if c_pos[0] > 0:
            # Only works if multi-line
            self.text_field.buffer.cursor_down(c_pos[0])
        self.text_field.buffer.cursor_right(c_pos[1])

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
            self.application_state.current_path = path

    def show_message(self, title: str, text: str, centered: bool = True) -> None:
        """Shows about message"""
        if centered:
            text = text.split("\n")
            text = "\n".join(map(lambda x: x.center(DIALOG_WIDTH - 5), text))

        async def coroutine(self: MenuNav) -> None:
            dialog = MessageDialog(title, text)
            await self.show_dialog_as_float(dialog)

        ensure_future(coroutine(self))

    async def show_dialog_as_float(
        self, dialog: PopUpDialog
    ) -> Optional[Union[str, bool]]:
        """Focuses a dialog. Returns the dialog's future. Then refocuses the original window."""
        float_ = Float(content=dialog)
        # Put given dialog on top of everything
        self.root_container.floats.insert(0, float_)

        app = get_app()

        # Put current window in a temp variable
        focused_before = app.layout.current_window
        # Focus cursor to the given dialog
        app.layout.focus(dialog)
        # Wait for the dialog to finish and stores the future's result
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

        @bindings.add("c-e")
        def convert_to_emoji(event: KeyPressEvent) -> None:
            """Convert text to emoji using Ctrl-E"""
            self.do_convert_to_emoji()

        return bindings
