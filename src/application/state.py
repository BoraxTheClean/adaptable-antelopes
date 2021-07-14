import json


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
            with open("user_setting.json", "r") as j:
                self.user_settings = json.loads(j.read())
        except FileNotFoundError:
            # if for some reason the file is deleted but then i need to maintain all the setting here
            self.user_settings = {"last_path": None, "style": ""}  # color picker?
            with open("user_setting.json", "w") as j:
                default_user_settings = json.dumps(self.user_settings)
                j.write(default_user_settings)

        self.show_status_bar = True
        if "last_path" in self.user_settings and self.user_settings["last_path"]:
            self.current_path = self.user_settings["last_path"]
        else:
            self.current_path = None
