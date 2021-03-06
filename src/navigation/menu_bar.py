import datetime
import json
import os
import shutil
import webbrowser
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
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import MenuContainer, MenuItem

from constants import DIALOG_WIDTH, NOTES_DIR, USER_SETTINGS_DIR
from custom_types import (
    ColorPicker,
    ConfirmDialog,
    MessageDialog,
    PopUpDialog,
    SaveExitDialog,
    ScrollMenuColorDialog,
    ScrollMenuDialog,
    TextInputDialog,
)
from utils import display_path, get_unique_filename


class MenuNav:
    """Menu bar

    Displays menu items

    Handles every action related to menu items

    Handles key bindings for some actions
    """

    def __init__(self):
        """Create the menu items"""
        self.root_container = MenuContainer(
            body=self.body,
            menu_items=[
                MenuItem(
                    "File",
                    children=[
                        MenuItem("New Note", handler=self.do_new_file),
                        MenuItem("Open Note", handler=self.do_scroll_menu),
                        MenuItem("Save", handler=self.do_save_file),
                        MenuItem("Save as...", handler=self.do_save_as_file),
                        MenuItem("-", disabled=True),
                        MenuItem("New Folder", handler=self.do_new_folder),
                        MenuItem("-", disabled=True),
                        MenuItem("Move...", handler=self.do_move_item),
                        MenuItem("Rename...", handler=self.do_rename_item),
                        MenuItem("Delete...", handler=self.do_delete_item),
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
                        MenuItem("Select All", handler=self.do_select_all),
                        MenuItem("Time/Date", handler=self.do_time_date),
                        MenuItem("Text To Emoji", handler=self.do_convert_to_emoji),
                    ],
                ),
                MenuItem(
                    "View",
                    children=[
                        MenuItem("Status Bar", handler=self.do_status_bar),
                        MenuItem("Open Link", handler=self.do_open_link),
                        MenuItem("Color Settings", handler=self.do_color_scroll),
                        MenuItem(
                            "Reset to default styles", handler=self.do_reset_styles
                        ),
                    ],
                ),
                MenuItem(
                    "Info",
                    children=[
                        MenuItem("About", handler=self.do_about),
                        MenuItem("Shortcuts", handler=self.do_show_shortcuts),
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

    ############ HANDLERS FOR MENU ITEMS ############
    def do_save_file(self) -> None:
        """Try to save. If no file is being edited, save as instead to create a new one."""
        if path := self.application_state.current_path:
            self._save_file_at_path(path, self.text_field.text)
        else:
            self.do_save_as_file()

    def do_save_as_file(self) -> None:
        """Try to Save As a file under a new name/path."""

        async def coroutine(self: MenuNav) -> None:
            """
            Prompt the user for a file path to save their note.

            If the path entered is a valid file name, save the current note at that path.
            """
            has_folders = any(
                os.path.isdir(os.path.join(NOTES_DIR, f)) for f in os.listdir(NOTES_DIR)
            )
            if has_folders:
                dialog = ScrollMenuDialog(
                    title="Save As",
                    text="Choose the location of the file.",
                    directory=self.application_state.current_dir,
                    show_files=False,
                )
                directory = await self.show_dialog_as_float(dialog)
                if not directory:
                    return
            else:
                # Skip the scroll menu if there are no folders yet (to not confuse users)
                directory = NOTES_DIR

            open_dialog = TextInputDialog(
                title="Save As", label_text="Enter the name of the file:"
            )
            file_name = await self.show_dialog_as_float(open_dialog)
            if file_name is None:
                return

            # Validate that the file name:
            # 1. Is not the empty string or None
            # 2. Doesn't consist exclusively of whitespace
            # 3. Doesn't start with "."
            # 4. Doesn't contain "/" or "\\"
            if (
                file_name
                and not file_name.isspace()
                and not file_name.startswith(".")
                and not any(x in file_name for x in ("/", "\\"))
            ):
                if not any(file_name.endswith(x) for x in (".txt", ".md")):
                    file_name += ".txt"
                path = os.path.join(directory, file_name)

                if os.path.isfile(path):
                    open_dialog = ConfirmDialog(
                        title="Save As",
                        text=f"The file {path} already exists. Do you want to overwrite it?",
                    )
                    override = await self.show_dialog_as_float(open_dialog)
                    if not override:
                        return

                self._save_file_at_path(path, self.text_field.text)
            else:
                self.show_message("Invalid Name", "Please enter a valid file name.")

        ensure_future(coroutine(self))

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

                    set_title(f"ThoughtBox - {display_path(path)}")
                else:
                    # Else show a popup message revealing the error message
                    self.show_message(
                        title="extension_error",
                        text="Unsupported file extension. Only '.txt' and '.md' are supported",
                    )

        ensure_future(coroutine(self))

    def do_about(self) -> None:
        """About from menu select"""
        self.show_message(
            "About",
            "ThoughtBox\n"
            + "Created by Adaptable Antelopes.\n"
            + "--------------------\n\n"
            + "Welcome to thinking inside the box\n",
        )

    def do_new_file(self) -> None:
        """Make a new file"""
        self.text_field.text = ""
        self.application_state.current_path = None
        set_title("ThoughtBox - Untitled")

    def do_move_item(self) -> None:
        """Move a folder or file to a different directory."""

        async def coroutine(self: MenuNav) -> None:
            dialog = ScrollMenuDialog(
                title="Move Item",
                text="Choose the folder/note you want to move.",
                directory=self.application_state.current_dir,
                show_files=True,
            )
            item_path = await self.show_dialog_as_float(dialog)
            if not item_path:
                return

            if item_path == NOTES_DIR:
                return self.show_message(
                    title="Move Item",
                    text="You cannot move the root folder.",
                )

            dialog = ScrollMenuDialog(
                title="Move Item",
                text="Choose the location where you want to move the item to.",
                directory=self.application_state.current_dir,
                show_files=False,
            )
            move_path = await self.show_dialog_as_float(dialog)
            if not move_path:
                return

            if os.path.exists(os.path.join(move_path, os.path.basename(item_path))):
                return self.show_message(
                    title="Move Item",
                    text=f"{os.path.basename(item_path)} already exists at that location.",
                )

            try:
                shutil.move(item_path, move_path)
            except OSError:
                self.show_message(
                    title="Move Item",
                    text="Unable to move item to that location.",
                )
            else:
                if (
                    current_path := self.application_state.current_path
                ) and current_path.startswith(item_path):
                    set_title(f"ThoughtBox - {display_path(current_path)} (Moved)")
                    self.application_state.current_path = None
                self.show_message(
                    title="Move Item",
                    text=f"Item successfully moved to {move_path}.",
                )

        ensure_future(coroutine(self))

    def do_new_folder(self) -> None:
        """Creates a folder"""

        async def coroutine(self: MenuNav) -> None:
            has_folders = any(
                os.path.isdir(os.path.join(NOTES_DIR, f)) for f in os.listdir(NOTES_DIR)
            )
            if has_folders:
                dialog = ScrollMenuDialog(
                    title="New Folder",
                    text="Choose the location of the new folder.",
                    directory=self.application_state.current_dir,
                    show_files=False,
                )
                path = await self.show_dialog_as_float(dialog)
                if not path:
                    return
            else:
                # Skip the scroll menu if there are no folders yet (to not confuse users)
                path = NOTES_DIR

            dialog = TextInputDialog(
                "New Folder", label_text="Enter the name of the new folder:"
            )
            folder_name = await self.show_dialog_as_float(dialog)
            if folder_name is None:
                return

            # Validate that the folder name:
            # 1. Is not the empty string or None
            # 2. Doesn't consist exclusively of whitespace
            # 3. Doesn't start with "."
            # 4. Doesn't contain "/" or "\\"
            if (
                folder_name
                and not folder_name.isspace()
                and not folder_name.startswith(".")
                and not any(x in folder_name for x in ("/", "\\"))
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

    def do_rename_item(self) -> None:
        """Renames a folder/note"""

        async def coroutine(self: MenuNav) -> None:
            dialog = ScrollMenuDialog(
                title="Rename Item",
                text="Choose the folder/note you want to rename.",
                directory=self.application_state.current_dir,
                show_files=True,
                path=self.application_state.current_dir,
            )
            path = await self.show_dialog_as_float(dialog)
            if not path:
                return

            if path == NOTES_DIR:
                return self.show_message(
                    title="Rename Item",
                    text="You cannot rename the root folder.",
                )

            dialog = TextInputDialog(
                "Rename Item", label_text="Enter the new name of the folder/note:"
            )
            new_name = await self.show_dialog_as_float(dialog)
            if new_name is None:
                return

            # Validate that the folder name:
            # 1. Is not the empty string or None
            # 2. Doesn't consist exclusively of whitespace
            # 3. Doesn't start with "."
            # 4. Doesn't contain "/" or "\\"
            # 5. Ends with ".txt" or ".md" if the original path was a file
            if (
                new_name
                and not new_name.isspace()
                and not new_name.startswith(".")
                and not any(x in new_name for x in ("/", "\\"))
                and (
                    os.path.isdir(path)
                    or any(new_name.endswith(x) for x in (".txt", ".md"))
                )
            ):
                new_path = os.path.join(os.path.dirname(path), new_name)
                if os.path.exists(new_path):
                    return self.show_message(
                        title="Rename Item", text="That folder/note already exists."
                    )

                try:
                    os.rename(path, new_path)
                except OSError:
                    self.show_message(
                        title="Rename Item",
                        text="Please enter a valid name.",
                    )
                else:
                    if (
                        current_path := self.application_state.current_path
                    ) and current_path.startswith(path):
                        set_title(f"ThoughtBox - {display_path(current_path)} (Moved)")
                        self.application_state.current_path = None
                    self.show_message(
                        title="Rename Item",
                        text=f"{path} was successfully renamed to {new_path}.",
                    )
            else:
                text = "Please enter a valid name."
                if os.path.isfile(path):
                    text += " Files must end with '.txt' or '.md'"
                self.show_message(
                    title="Rename Item",
                    text=text,
                )

        ensure_future(coroutine(self))

    def do_delete_item(self) -> None:
        """Delete a folder/note"""

        async def coroutine(self: MenuNav) -> None:
            dialog = ScrollMenuDialog(
                title="Delete Item",
                text="Choose the item you want to delete.",
                directory=self.application_state.current_dir,
                show_files=True,
                path=self.application_state.current_dir,
            )

            path = await self.show_dialog_as_float(dialog)
            if not path:
                return

            if path == NOTES_DIR:
                return self.show_message(
                    title="Delete Item",
                    text="You cannot delete the root folder.",
                )

            text = f"Are you sure you want to delete {path}"
            if os.path.isdir(path):
                text += "\nand all of its contents"
            dialog = ConfirmDialog(
                title="Delete Item",
                text=text + "?",
            )
            confirm_delete = await self.show_dialog_as_float(dialog)

            if confirm_delete:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    elif os.path.isfile(path):
                        os.remove(path)
                    else:
                        raise ValueError(
                            "Selected path is neither a file nor directory."
                        )
                except OSError:
                    self.show_message(
                        title="Delete Folder",
                        text="Failed to delete the folder.",
                    )
                else:
                    if (
                        current_path := self.application_state.current_path
                    ) and current_path.startswith(path):
                        set_title(
                            f"ThoughtBox - {display_path(current_path)} (Deleted)"
                        )
                        self.application_state.current_path = None
                    self.show_message(
                        title="Delete Folder",
                        text=f"{path} was successfully deleted.",
                    )

        ensure_future(coroutine(self))

    def do_exit(self) -> None:
        """Exit app, with warning if current file unsaved"""

        async def coroutine(self: MenuNav) -> None:
            title = "Unsaved Changes"
            # If file previously saved, check if current version matches saved
            if (
                current_path_valid := self.application_state.current_path
                and os.path.exists(self.application_state.current_path)
            ):
                text = "\n".join(
                    (
                        f"The file {self.application_state.current_path}",
                        "contains unsaved changes. Save before exit?",
                    )
                )
                with open(self.application_state.current_path) as f:
                    written = f.read()
                unsaved_changes = written != self.text_field.text
            # If file not previously saved, warn if contains any text
            else:
                text = "This file has not yet been saved. Save before exit?"
                unsaved_changes = self.text_field.text != ""
            if unsaved_changes:
                dialog = SaveExitDialog(title=title, text=text)
                choice = await self.show_dialog_as_float(dialog)
            else:
                choice = "nosave"
            if choice != "cancel":
                if choice == "save":
                    # If not yet saved, generate generic name to save to
                    if not current_path_valid:
                        self.application_state.current_path = os.path.join(
                            NOTES_DIR, get_unique_filename(NOTES_DIR)
                        )
                    self.do_save_file()
                # Exit
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

        ensure_future(coroutine(self))

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

    def do_color_scroll(self) -> None:
        """Open Scroll Menu"""

        async def coroutine(self: MenuNav) -> None:
            # first scroll dialog
            style_class_attr = "back"
            style_class = ""
            while (
                style_class_attr == "back"
                and style_class != "cancel"
                and style_class_attr != "cancel"
            ):
                dialog = ScrollMenuColorDialog()
                style_class = await self.show_dialog_as_float(dialog)
                if style_class != "cancel":
                    # second dialog
                    dialog = ScrollMenuColorDialog(inner=True)
                    style_class_attr = await self.show_dialog_as_float(dialog)
            if style_class == "cancel":
                pass

            elif style_class_attr != "cancel":
                color_input_dialog = ColorPicker(style_class, style_class_attr)
                await self.show_dialog_as_float(color_input_dialog)

                # just loads any style back if any change were saved it will keep them loaded
                with open(USER_SETTINGS_DIR, "r") as user_file:
                    user_settings = json.load(user_file)

                style_dict = user_settings["style"]
                get_app().style = Style.from_dict(style_dict)

            else:
                # else canceled
                pass

        ensure_future(coroutine(self))

    def do_reset_styles(self) -> None:
        """Reset to default color settings"""

        async def coroutine(self: MenuNav) -> None:
            open_dialog = ConfirmDialog(
                title="Reset Styles",
                text="Are you sure you want to reset to default color settings?",
            )
            confirm = await self.show_dialog_as_float(open_dialog)
            if not confirm:
                return

            self.application_state._load_settings(reset_style=True)
            self.show_message(
                title="Reset Styles", text="Successfully reset color settings."
            )
            with open(USER_SETTINGS_DIR, "r") as f:
                styles = json.load(f)["style"]
            get_app().style = Style.from_dict(styles)

        ensure_future(coroutine(self))

    def do_find(self) -> None:
        """Find"""
        start_search(self.text_field.control)

    def do_find_next(self) -> None:
        """Find next"""
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
        """Toggles status bar"""
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

    def do_open_link(self) -> None:
        """Validate whether link is internal or external and open the link to the browser (or in the app)"""
        if word := self.text_field.document.get_word_under_cursor(WORD=True):
            # Validate url (whether internal or external)
            # Then open in new tab
            webbrowser.open_new_tab(word)

    def do_show_shortcuts(self) -> None:
        """Open a popup to show the shortcuts"""
        self.show_message(
            "Shortcuts",
            (
                "ESC: Focus cursor on the text field\n"
                "CTRL+K: Open Menu.\n"
                "CTRL+N: Start a new file\n"
                "CTRL+S: Save current file\n"
                "CTRL+O: Open an existing note\n"
                "CTRL+Q: Exit the application\n"
                "CTRL+A: Select All\n"
                "CTRL+Z: Undo\n"
                "CTRL+E: Turn text like :smile: into emoji\n"
                "ALT+O: Open link under cursor"
            ),
            centered=False,
        )

    ############ HELPER FUNCTIONS #############
    def _save_file_at_path(self, path: str, text: str) -> None:
        """Saves text (changes) to a file path"""
        try:
            with open(path, "w", encoding="utf8") as f:
                f.write(text)
        except IOError as e:
            self.show_message("Error", "{}".format(e))
        else:
            set_title(f"ThoughtBox - {display_path(path)}")
            self.application_state.current_path = path

    def show_message(self, title: str, text: str, centered: bool = True) -> None:
        """Shows About message"""
        # Align text content center
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
        """Focuses a dialog. Returns the dialog's future. Then refocuses the original window"""
        float_ = Float(content=dialog)
        # Put given dialog on top of everything
        self.root_container.floats.insert(0, float_)

        # Get currently active application
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
        """Setup Keyboard Shortcuts"""
        bindings = KeyBindings()

        @bindings.add("c-k")
        def open_menu(event: KeyPressEvent) -> None:
            """Focus menu with Ctrl-K"""
            event.app.layout.focus(self.root_container.window)

        @bindings.add("escape")
        def close_menu(event: KeyPressEvent) -> None:
            """Focus text field"""
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
            """Exit application with Ctrl-Q"""
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

        @bindings.add("escape", "o")
        def open_link(event: KeyPressEvent) -> None:
            """Open a clickable link using Alt-O"""
            self.do_open_link()

        return bindings
