import json
import os

from constants import NOTES_DIR, WELCOME_PAGE


class ApplicationState:
    """Holds things like settings and current path in an object"""

    def __init__(self):
        try:
            with open(os.path.join(NOTES_DIR, ".user_setting.json"), "r") as f:
                self.user_settings = json.load(f)
        except FileNotFoundError:
            # if for some reason the file is deleted but then i need to maintain all the setting here
            # no style dict atm for users prefs not used anywhere yet
            self.user_settings = {"last_path": None, "style": ""}  # color picker?
            with open(os.path.join(NOTES_DIR, ".user_setting.json"), "w") as j:
                default_user_settings = json.dumps(self.user_settings)
                j.write(default_user_settings)

        self.show_status_bar = True
        if self.user_settings.get("last_path"):
            self.current_path = self.user_settings["last_path"]
        else:
            # Open the welcome page
            self.current_path = NOTES_DIR + "/" + WELCOME_PAGE
