import json
import os

from constants import NOTES_DIR, USER_SETTINGS_DIR


class ApplicationState:
    """
    Application state.

    For the simplicity, we store this as a global, but better would be to
    instantiate this as an object and pass at around.
    """

    # def __init__(self):
    #     self.show_status_bar = True
    #     self.current_path = None

    def __init__(self):
        self.current_path = None
        try:
            with open(USER_SETTINGS_DIR, "r") as j:
                self.user_settings = json.loads(j.read())
        except FileNotFoundError:
            # if for some reason the file is deleted but then i need to maintain all the setting here
            # no style dict atm for users prefs not used anywhere yet
            default_style = {
                # 'text-area': "bg:#00a444",
                # "top": "bg:#00bb00",
                "frame-label": "bg:#ffffff #000000",
                "status": "reverse",
                "shadow": "bg:#000000 #ffffff",
                # "menu": "shadow:#440044",
                "menu": "bg:#004444",
                "menu-bar": "bg:#00ff00",
                # "menu.": "#00ff00",
                # "button" : "bg:#004444"
                # 'text-field': "#00ff00 bg:#000000",
                "dialog.body": "bg:#111111 #00aa44",
            }

            self.user_settings = {"last_path": os.path.join(NOTES_DIR, 'welcome.md'), "style": default_style}
            with open(USER_SETTINGS_DIR, "w") as j:
                default_user_settings = json.dumps(self.user_settings)
                j.write(default_user_settings)

        self.show_status_bar = True
        if "last_path" in self.user_settings and self.user_settings["last_path"]:
            self.current_path = self.user_settings["last_path"]
        else:
            self.current_path = None
