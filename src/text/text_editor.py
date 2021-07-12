#!/usr/bin/env python
"""A simple example of a Notepad-like text editor."""
import datetime
from asyncio import Future, ensure_future

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer
from prompt_toolkit.search import start_search
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label,
    MenuContainer,
    MenuItem,
    SearchToolbar,
    TextArea,
)

from custom_types.ui_types import PopUpDialog
from scroll.scroll_menu import ScrollMenuDialog


class ApplicationState:
    """
    Application state.

    For the simplicity, we store this as a global, but better would be to
    instantiate this as an object and pass at around.
    """

    show_status_bar = True
    current_path = None


# TODO make something like this that will pull up the side file menu
def get_status_bar_left_text() -> None:
    """Display current file's name"""
    if name := text_field.buffer.name:
        return name
    return "Editor - Untitled"


def get_statusbar_middle_text() -> None:
    """Gets status bar opens menu"""
    return " Press Ctrl-K to open menu. "


def get_statusbar_right_text() -> None:
    """Get status bar for the right text?"""
    return " {}:{}  ".format(
        text_field.document.cursor_position_row + 1,
        text_field.document.cursor_position_col + 1,
    )


search_toolbar = SearchToolbar()
text_field = TextArea(
    lexer=DynamicLexer(
        lambda: PygmentsLexer.from_filename(
            ApplicationState.current_path or ".txt", sync_from_start=False
        )
    ),
    scrollbar=True,
    search_field=search_toolbar,
)


class TextInputDialog(PopUpDialog):
    """Text Input for the open dialog box"""

    # unsure for type of completer guessing pathcompleter
    def __init__(
        self, title: str = "", label_text: str = "", completer: PathCompleter = None
    ):
        self.future = Future()

        def accept_text(buf: object) -> bool:
            """Accepts text"""
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept() -> None:
            """Accept"""
            self.future.set_result(self.text_area.text)

        def cancel() -> None:
            """Cancel"""
            self.future.set_result(None)

        self.text_area = TextArea(
            completer=completer,
            multiline=False,
            width=D(preferred=40),
            accept_handler=accept_text,
        )

        ok_button = Button(text="OK_open", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


class MessageDialog(PopUpDialog):
    """About tab dialog box"""

    def __init__(self, title: str, text: str):
        self.future = Future()

        def set_done() -> None:
            """Future object when done return None"""
            self.future.set_result(None)

        # changed text from OK to see where this is
        ok_button = Button(text="OK_Msg_Dialog", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


body = HSplit(
    [
        text_field,
        search_toolbar,
        ConditionalContainer(
            content=VSplit(
                [
                    Window(
                        FormattedTextControl(get_status_bar_left_text),
                        style="class:status",
                        align=WindowAlign.LEFT,
                    ),
                    Window(
                        FormattedTextControl(get_statusbar_middle_text),
                        style="class:status",
                    ),
                    Window(
                        FormattedTextControl(get_statusbar_right_text),
                        style="class:status.right",
                        width=9,
                        align=WindowAlign.RIGHT,
                    ),
                ],
                height=1,
            ),
            filter=Condition(lambda: ApplicationState.show_status_bar),
        ),
    ]
)

# Global key bindings.
bindings = KeyBindings()


@bindings.add("c-k")
def _(event: object) -> None:
    """Focus menu."""
    event.app.layout.focus(root_container.window)


@bindings.add("escape")
def _(event: object) -> None:
    """Focus text field."""
    event.app.layout.focus(text_field)


#
# Handlers for menu items.
#


def do_open_file() -> None:
    """Open file from menu select"""

    async def coroutine() -> None:
        open_dialog = TextInputDialog(
            title="Open file",
            label_text="Enter the path of a file:",
            completer=PathCompleter(),
        )

        path = await show_dialog_as_float(open_dialog)
        ApplicationState.current_path = path

        if path is not None:
            try:
                with open(path, "rb") as f:
                    text_field.text = f.read().decode("utf-8", errors="ignore")
                    # Save the name to be display in the title
                    text_field.buffer.name = path
            except IOError as e:
                show_message("Error", "{}".format(e))

    ensure_future(coroutine())


def do_scroll_menu() -> None:
    """Open Scroll Menu"""
    show_scroll("Scroll", "buf")


def show_scroll(title: str, text: str) -> None:
    """Shows about message"""

    async def coroutine() -> None:
        dialog = ScrollMenuDialog(title, text)
        await show_dialog_as_float(dialog)

    ensure_future(coroutine())


def do_about() -> None:
    """About from menu select"""
    show_message("About", "Text editor demo.\nCreated by Jonathan Slenders.")


def show_message(title: str, text: str) -> None:
    """Shows about message"""

    async def coroutine() -> None:
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)

    ensure_future(coroutine())


async def show_dialog_as_float(dialog: PopUpDialog) -> None:
    """Coroutine what does it return idk? the messageDialogs future result which is None?"""
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


# All the do_ is a menu item

# TODO actually make new file
def do_new_file() -> None:
    """Doesn't make new file just clears text_field but i guess thats fine till save"""
    text_field.text = ""


def do_exit() -> None:
    """Exit"""
    get_app().exit()


def do_time_date() -> None:
    """Inserts current datetime into text_field from menu"""
    text = datetime.datetime.now().isoformat()
    text_field.buffer.insert_text(text)


def do_go_to() -> None:
    """Go to line"""

    async def coroutine() -> None:
        dialog = TextInputDialog(title="Go to line", label_text="Line number:")

        line_number = await show_dialog_as_float(dialog)

        try:
            line_number = int(line_number)
        except ValueError:
            show_message("Invalid line number")
        else:
            text_field.buffer.cursor_position = (
                text_field.buffer.document.translate_row_col_to_index(
                    line_number - 1, 0
                )
            )

    ensure_future(coroutine())


def do_undo() -> None:
    """Undo"""
    text_field.buffer.undo()


def do_cut() -> None:
    """Cut"""
    data = text_field.buffer.cut_selection()
    get_app().clipboard.set_data(data)


def do_copy() -> None:
    """Copy"""
    data = text_field.buffer.copy_selection()
    get_app().clipboard.set_data(data)


def do_delete() -> None:
    """Delete"""
    text_field.buffer.cut_selection()


def do_find() -> None:
    """Find"""
    start_search(text_field.control)


def do_find_next() -> None:
    """Fine next"""
    search_state = get_app().current_search_state

    cursor_position = text_field.buffer.get_search_position(
        search_state, include_current_position=False
    )
    text_field.buffer.cursor_position = cursor_position


def do_paste() -> None:
    """Paste"""
    text_field.buffer.paste_clipboard_data(get_app().clipboard.get_data())


def do_select_all() -> None:
    """Select all"""
    text_field.buffer.cursor_position = 0
    text_field.buffer.start_selection()
    text_field.buffer.cursor_position = len(text_field.buffer.text)


def do_status_bar() -> None:
    """Opens ar closes status bar"""
    ApplicationState.show_status_bar = not ApplicationState.show_status_bar


#
# The menu container.
#


root_container = MenuContainer(
    body=body,
    menu_items=[
        MenuItem(
            "File",
            children=[
                MenuItem("New...", handler=do_new_file),
                #MenuItem("Open...", handler=do_open_file),
                MenuItem("Open Scroll", handler=do_scroll_menu),
                # TODO add save functionality implement do_save and do_save as
                MenuItem("Save"),
                MenuItem("Save as..."),
                MenuItem("-", disabled=True),
                MenuItem("Exit", handler=do_exit),
            ],
        ),
        MenuItem(
            "Edit",
            children=[
                MenuItem("Undo", handler=do_undo),
                MenuItem("Cut", handler=do_cut),
                MenuItem("Copy", handler=do_copy),
                MenuItem("Paste", handler=do_paste),
                MenuItem("Delete", handler=do_delete),
                MenuItem("-", disabled=True),
                MenuItem("Find", handler=do_find),
                MenuItem("Find next", handler=do_find_next),
                # TODO no replace function we can just delete it or try to implement do_replace
                MenuItem("Replace"),
                MenuItem("Go To", handler=do_go_to),
                MenuItem("Select All", handler=do_select_all),
                MenuItem("Time/Date", handler=do_time_date),
            ],
        ),
        MenuItem(
            "View",
            children=[MenuItem("Status Bar", handler=do_status_bar)],
        ),
        MenuItem(
            "Info",
            children=[
                MenuItem("About", handler=do_about),

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
    key_bindings=bindings,
)

# style of menu can def play around here
style = Style.from_dict(
    {
        "status": "reverse",
        "shadow": "bg:#440044",
    }
)

layout = Layout(root_container, focused_element=text_field)

application = Application(
    layout=layout,
    enable_page_navigation_bindings=True,
    style=style,
    mouse_support=True,
    full_screen=True,
)


def run() -> None:
    """Run"""
    application.run()