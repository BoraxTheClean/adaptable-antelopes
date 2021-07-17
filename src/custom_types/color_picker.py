import functools
import json
import string
from asyncio import Future

from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import FormattedTextControl, ScrollablePane
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Button, Dialog, Frame, Label, TextArea

from constants import USER_SETTINGS_DIR
from custom_types.ui_types import PopUpDialog

# class UserSettings():
#     def __init__(self, dict):
#         self.last_path = None
#         self.style_dict = set_style_dict()
#
#
#     def set_style_dict(self):
#
#
#     def style_to_dict(self):
#         for key in self.style_dict.keys():
#             style_attr = self.style_dict[key].split(' ')
#             if len(style_attr) == 1:
#                 pass
#             else:
#                 style_dict[key] = style_attr[]
#
#     def dict_to_style(self):


class ColorPicker(PopUpDialog):
    """Text Input for the open dialog box"""

    def __init__(self, style_class: str):
        self.future = Future()
        with open(USER_SETTINGS_DIR, "r") as user_file:
            self.user_settings = json.load(user_file)

        def is_hex(s: str) -> bool:
            """Validate that the user entered text is a 6 digit hex number

            1. len(6)
            2. only contains 0-9 and a-f
            """
            if len(s) == 6:
                hex_digits = set(string.hexdigits)
                # if s is long, then it is faster to check against a set
                return all(c in hex_digits for c in s)
            else:
                return False

        def string_to_dict(s: str) -> dict:
            out = {}
            items = s.split(" ")
            for elm in items:
                key, pair = elm.split("#")
                out[key.replace(":", "")] = "#" + pair
            return out

        def dict_to_string(d: dict) -> str:
            out = ""
            for key, pair in d.items():
                if key == "":
                    out += key + pair
                else:
                    out += key + ":" + pair
                out += " "
            return out[:-1]

        def prev() -> None:
            if is_hex(self.text_area.text):
                if style_class == "text":
                    # TODO parse the list of strings in each style dict entry
                    for keys in self.user_settings["style"].keys():
                        if keys != "shadow" and keys != "status" and keys != "menu-bar":
                            style_menu = self.user_settings["style"][keys]
                            style_menu_dict = string_to_dict(style_menu)
                            style_menu_dict[""] = f"#{self.text_area.text}"
                            style_menu = dict_to_string(style_menu_dict)
                            self.user_settings["style"][keys] = style_menu
                    # style_menu[0] + f"#{self.text_area.text}
                    # "menu": "bg:#004400 #ffffff",
                    # self.user_settings["style"]['menu'] = f"#{self.text_area.text}" # im over-riding menu
                    # self.user_settings["style"]['dialog'] = f"#{self.text_area.text}"

                    get_app().style = Style.from_dict(self.user_settings["style"])
                    self.sample_window.style = f"#{self.text_area.text}"
                    self.promp_label.text = "Enter a hex:"
                else:
                    self.user_settings["style"][
                        style_class
                    ] = f"bg:#{self.text_area.text}"
                    get_app().style = Style.from_dict(self.user_settings["style"])
                    self.sample_window.style = f"bg:#{self.text_area.text}"
                    self.promp_label.text = "Enter a hex:"
            else:
                self.promp_label.text = "Invalid Hex!"

        def accept_text(buf: Buffer) -> bool:
            prev()
            buf.complete_state = None
            return True

        def accept() -> None:
            """Accept"""
            if is_hex(self.text_area.text):
                # save to user settings
                self.user_settings["style"][style_class] = f"bg:#{self.text_area.text}"

                with open(USER_SETTINGS_DIR, "w") as user_file:
                    user_file.write(json.dumps(self.user_settings))

                self.future.set_result(None)
            else:
                # invalid hex don't set_future
                self.promp_label.text = "Invalid Hex"

        def cancel() -> None:
            """Cancel"""
            self.future.set_result(None)

        self.text_area = TextArea(
            multiline=False,
            width=D(preferred=6),
            accept_handler=accept_text,
        )

        self.promp_label = Label(text="Enter a hex:")
        self.sample_window = Window(content=FormattedTextControl("Hello"))

        preview_button = Button(text="Preview", handler=prev)
        ok_button = Button(text="Apply", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title="Pick A Color",
            body=HSplit([self.promp_label, self.text_area, self.sample_window]),
            buttons=[preview_button, ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


class ScrollMenuColorDialog(PopUpDialog):
    """Scroll menu added to the info tab dialog box

    {
    "frame-label": "bg:#ffffff #000000",
    "status": "reverse",
    "shadow": "bg:#000000 #ffffff",
    "menu": "bg:#004400",
    "menu-bar": "bg:#00ff00",
    "dialog.body": "bg:#111111 #00aa44",}
    """

    def __init__(self):
        """Initialize Scroll Menu Dialog

        Args:
            commander (object): Instance of ThoughtBox (required for modifying text in the editor)
        """
        self.future = Future()

        # ["frame-label", 'text', "menu", "menu-bar", "dialog.body", 'shadow']
        style_list = [
            "shadow",
            "menu",
            "text",
            "menu-bar",
            "button",
            "dialog.body",
            "dialog",
        ]

        def set_cancel() -> bool:
            """Cancel"""
            self.future.set_result(False)

        def set_style_class(style_element: str) -> None:
            """Passes the chosen style class to the menu_bar"""
            self.future.set_result(style_element)

        self.body = Frame(
            ScrollablePane(
                HSplit(
                    [
                        Frame(
                            Button(
                                text=style_class,
                                handler=functools.partial(set_style_class, style_class),
                                width=20,
                            )
                        )
                        for style_class in style_list
                    ]
                )
                # ScrollablePane(HSplit([TextArea(text=f"label-{i}") for i in range(20)]))
            )
        )

        # Add chosen file to editor
        # self.ok_button = Button(text="OK", handler=(lambda: set_done()))
        self.cancel_button = Button(text="Cancel", handler=(lambda: set_cancel()))

        self.dialog = Dialog(
            title="Color Picker",
            body=self.body,
            buttons=[self.cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
