"""A simple example of a scrollable pane."""
import functools
import os
from os.path import isdir, isfile, join

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import (
    CompletionsMenu,
    Float,
    FloatContainer,
    FormattedTextControl,
    HSplit,
    Layout,
    ScrollablePane,
    VSplit,
    Window,
)
from prompt_toolkit.widgets import Button, Frame, Label


class ScrollableMenu:
    """
    Scrollable Menu UI Element.
    
    Displays contents of the a given working directory and allows users to inspect files. 
    In the future users can drill down into directories.
    """

    def __init__(self, dir: str):
        # Display contents in the current working directory on the menu
        cwd_content = os.listdir(dir)
        frames = [
            Frame(
                Button(
                    text=item,
                    handler=functools.partial(self.display_content, item, "."),
                )
            )
            for item in cwd_content
        ]

        self.body = VSplit(
            children=[
                Label(text="File's content here"),
                Frame(ScrollablePane(HSplit(children=frames))),
            ],
            padding_char="|",
            padding=1,
        )

    def display_content(self, target_content: str, target_dir: str) -> None:
        """Display content.

        If target's content is a file, display it in the left column.
        TODO: If the target_content is a directory, replace the right column with its content.

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
            pass
        else:
            raise ValueError("The target' content is neither a file or directory")


def setup_key_bindings() -> KeyBindings:
    """Set up key bindings for the root container"""
    kb = KeyBindings()

    @kb.add("c-c")
    def exit_(event: str) -> None:
        get_app().exit()

    kb.add("tab")(focus_next)
    kb.add("s-tab")(focus_previous)
    return kb


def main() -> None:
    """Create a big layout of many text areas, then wrap them in a `ScrollablePane`."""
    menu = ScrollableMenu(dir=".")

    root_container = FloatContainer(
        content=menu.body,
        floats=[
            Float(
                xcursor=True,
                ycursor=True,
                content=CompletionsMenu(max_height=16, scroll_offset=1),
            ),
        ],
    )

    layout = Layout(container=root_container)
    kb = setup_key_bindings()
    # Create and run application.
    application = Application(
        layout=layout, key_bindings=kb, full_screen=True, mouse_support=True
    )
    application.run()


if __name__ == "__main__":
    main()
