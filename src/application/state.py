import json
import os

from constants import NOTES_DIR, USER_SETTINGS_DIR, WELCOME_PAGE


class ApplicationState:
    """Holds things like settings and current path in an object"""

    def __init__(self):
        try:

            with open(USER_SETTINGS_DIR, "r") as j:
                self.user_settings = json.load(j)

        except FileNotFoundError:
            # if for some reason the file is deleted but then i need to maintain all the setting here
            # possible things to style
            default_style = {
                # 'text-area': "bg:#00a444",
                # "top": "bg:#00bb00",
                # "frame-label": "bg:#ffbbff #00bb00",
                "status": "reverse",
                "shadow": "bg:#000000 #00ff00",
                "menu": "bg:#abcdef",
                "text": "#000000",
                "menu-bar": "bg:#abcdef",
                "button": "bg:#004444",
                "dialog.body": "bg:#111111 #abcdef",
            }

            self.user_settings = {
                "last_path": os.path.join(NOTES_DIR, "welcome.md"),
                "style": default_style,
            }
            with open(USER_SETTINGS_DIR, "w") as j:
                json.dump(self.user_settings, j)

        self.show_status_bar = True
        if self.user_settings.get("last_path"):
            self.current_path = self.user_settings["last_path"]
        else:
            # Open the welcome page
            self.current_path = NOTES_DIR + "/" + WELCOME_PAGE

    @property
    def current_dir(self) -> str:
        """
        Returns the directory of the current path.

        If there is no current path, return NOTES_DIR
        """
        if self.current_path:
            return os.path.dirname(self.current_path)
        return NOTES_DIR
