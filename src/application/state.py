import json
import os
from typing import Dict

from constants import DEFAULT_STYLE, NOTES_DIR, USER_SETTINGS_DIR, WELCOME_PAGE


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

    def _load_settings(self, reset_style: bool = False) -> Dict[str, str]:
        """Load user settings from disk. Use default settings for any missing settings."""
        default_path = os.path.join(NOTES_DIR, "welcome.md")
        try:
            with open(USER_SETTINGS_DIR, "r") as f:
                # There is a failure case here, in that `.user_setting.json` could be an empty file.
                # In which case this raises a JSONDecodeError exception.
                # This should not be encountered in a normal user flow, but this is a risk.
                user_settings = json.load(f)
        except FileNotFoundError:
            # If for some reason the file is not present, then use the default settings and write them to disk.
            user_settings = {
                "last_path": default_path,
                "style": DEFAULT_STYLE,
            }
            with open(USER_SETTINGS_DIR, "w") as f:
                json.dump(user_settings, f)
            return user_settings
        else:
            if reset_style:
                user_settings["style"] = DEFAULT_STYLE
            with open(USER_SETTINGS_DIR, "w") as f:
                json.dump(user_settings, f)

        if "last_path" not in user_settings:
            user_settings["last_path"] = default_path
        if "style" not in user_settings or type(user_settings["style"]) is not dict:
            user_settings["style"] = DEFAULT_STYLE

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
