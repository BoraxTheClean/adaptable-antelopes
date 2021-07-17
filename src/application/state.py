import json
import os
from typing import Dict

from constants import NOTES_DIR, USER_SETTINGS_DIR, WELCOME_PAGE


class ApplicationState:
    """Holds things like settings and current path in an object"""

    def __init__(self):

        self.user_settings = self._load_settings()

        self.show_status_bar = True
        if self.user_settings.get("last_path"):
            self.current_path = self.user_settings["last_path"]
        else:
            # Open the welcome page
            self.current_path = NOTES_DIR + "/" + WELCOME_PAGE

    def _load_settings(self) -> Dict[str, any]:
        """Load user settings from disk. Use default settings for any missing settings."""
        default_style = {
            # 'text-area': "bg:#00a444",
            # "top": "bg:#00bb00",
            # "frame-label": "bg:#ffbbff #00bb00",
            "status": "reverse",
            "shadow": "bg:#000000 #00ff00",
            "menu": "bg:#abcdef",
            "menu-bar": "bg:#abcdef",
            "button": "bg:#004444",
            "dialog.body": "bg:#111111 #abcdef",
        }
        default_path = os.path.join(NOTES_DIR, "welcome.md")
        try:
            with open(USER_SETTINGS_DIR, "r") as j:
                # There is a failure case here, in that `.user_setting.json` could be an empty file.
                # In which case this raises a JSONDecodeError exception.
                # This should not be encountered in a normal user flow, but this is a risk.
                user_settings = json.load(j)
        except FileNotFoundError:
            # If for some reason the file is not present, then use the default settings and write them to disk.
            user_settings = {
                "last_path": default_path,
                "style": default_style,
            }
            with open(USER_SETTINGS_DIR, "w") as j:
                json.dump(user_settings, j)
            return user_settings
        if "last_path" not in user_settings:
            user_settings["last_path"] = default_path
        if "style" not in user_settings or type(user_settings["style"]) is not dict:
            user_settings["style"] = default_style
        return user_settings

    @property
    def current_dir(self) -> str:
        """
        Returns the directory of the current path.

        If there is no current path, return NOTES_DIR
        """
        if self.current_path:
            return os.path.dirname(self.current_path)
        return NOTES_DIR
