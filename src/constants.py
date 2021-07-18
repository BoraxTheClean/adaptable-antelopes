import os

NOTES_DIR = ".thought_box"
ASSETS_DIR = "src/assets"
WELCOME_PAGE = "welcome.md"
PADDING_CHAR = "|"
PADDING_WIDTH = 1
DIALOG_WIDTH = 80
USER_SETTINGS_DIR = os.path.join(NOTES_DIR, ".user_setting.json")
DEFAULT_STYLE = {
    "status": "reverse",
    "shadow": "bg:#000000 #ffffff",
    "menu": "bg:#22aa22",
    "menu-bar": "bg:#00ff00",
    "button": "bg:#004444 #abcdef",
    "dialog.body": "bg:#111111 #00aa44",
    "dialog": "#abcdef",
    "text-area": "",
    "frame-label": "bg:#ffffff #000000",
}
