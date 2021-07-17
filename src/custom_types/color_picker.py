import functools
import json
import string
from asyncio import Future

from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Button, Dialog, Frame, Label, TextArea

from constants import USER_SETTINGS_DIR
from custom_types.ui_types import PopUpDialog


class ColorPicker(PopUpDialog):
    """Text Input for the open dialog box"""

    def __init__(self, style_class: str, style_class_attr: str):
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
            return False

        def string_to_dict(s: str) -> dict:
            """Turns a single style classes string into a dict

            Ex 'bg:#123456 fg:#654321 #abcdef' -> {'bg':123456, 'fg':'654321', '':'abcdef'}
            """
            out = {}
            if len(s) == 0:
                return out
            items = s.split(" ")
            for elm in items:
                key, pair = elm.split("#")
                out[key.replace(":", "")] = "#" + pair
            return out

        def dict_to_string(d: dict) -> str:
            """Turns the style dict back to a single string"""
            out = ""
            for key, pair in d.items():
                if key == "":
                    out += key + pair
                else:
                    out += key + ":" + pair
                out += " "
            return out[:-1]

        def get_hex_style(style_c: str, style_c_attr: str) -> str:
            """Gets previously set hex value for user reference"""
            style_ = self.user_settings["style"][style_c]
            style_dict = string_to_dict(style_)
            if style_c_attr in style_dict.keys():
                # if key is real
                out = style_dict[style_c_attr].replace("#", "")
            else:
                out = ""
            return out

        def prev() -> None:
            """Preview the given change of style

            by setting it to applications style but not to the user_settings file
            """
            if is_hex(self.text_area.text):
                self.promp_label.text = "Enter a hex:"
                # just reset if it was set to Invalid

                style_menu = self.user_settings["style"][style_class]
                style_menu_dict = string_to_dict(style_menu)
                if style_class_attr != "":
                    # if class attribute is '' save as just #123456
                    style_menu_dict[""] = f"{style_class_attr}:#{self.text_area.text}"
                else:
                    style_menu_dict[""] = f"#{self.text_area.text}"
                style_menu = dict_to_string(style_menu_dict)
                self.user_settings["style"][style_class] = style_menu

                get_app().style = Style.from_dict(self.user_settings["style"])

            else:
                self.promp_label.text = "Invalid Hex!"

        def accept_text(buf: Buffer) -> bool:
            prev()
            buf.complete_state = None
            return True

        def accept() -> None:
            """Accept the change save the style to the user_settings file"""
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
            text=get_hex_style(style_class, style_class_attr),
            multiline=False,
            width=D(preferred=6),
            accept_handler=accept_text,
        )

        self.promp_label = Label(text="Enter a hex:")

        preview_button = Button(text="Preview", handler=prev)
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


class ScrollMenuColorDialog(PopUpDialog):
    """Scroll menu to pick which style you would like to change"""

    def __init__(self, inner: bool = False):
        """Initialize Scroll Menu Dialog

        Args:
            inner (bool) is the selection the outer style classes or the inner style class attributes
        """
        self.future = Future()

        style_list = [
            "shadow",
            "menu",
            "text-area",
            "menu-bar",
            "button",
            "dialog.body",
        ]

        def set_cancel() -> str:
            """Cancel return cancel so menu_bar knows to stop"""
            self.future.set_result("cancel")

        def set_class_attr(style_attr: str) -> None:
            """Selection of style class attribute"""
            self.future.set_result(style_attr)

        def set_style_class(style_element: str) -> None:
            """Passes the chosen style class to the menu_bar and resets body to be ready for next selection"""
            self.future.set_result(style_element)

        if not inner:
            # first menu selection
            self.body = Frame(
                ScrollablePane(
                    HSplit(
                        [
                            Frame(
                                Button(
                                    text=style_class,
                                    handler=functools.partial(
                                        set_style_class, style_class
                                    ),
                                    width=70,
                                )
                            )
                            for style_class in style_list
                        ]
                    )
                )
            )

        else:
            # second menu selection
            opt = ["bg", "fg", ""]
            opt_dic = {"bg": "background", "fg": "foreground", "": "text"}
            self.body = Frame(
                ScrollablePane(
                    HSplit(
                        [
                            Frame(
                                Button(
                                    text=opt_dic[class_attr],
                                    handler=functools.partial(
                                        set_class_attr, class_attr
                                    ),
                                    width=70,
                                )
                            )
                            for class_attr in opt
                        ]
                    )
                )
            )

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
