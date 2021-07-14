from typing import Optional


class ApplicationState:
    """
    Application state.

    For the simplicity, we store this as a global, but better would be to
    instantiate this as an object and pass at around.
    """

    show_status_bar = True
    current_path = None

    @staticmethod
    def get_current_path() -> Optional[str]:
        """Gets current path for scroll/scroll_menu to access"""
        return ApplicationState.current_path

    @staticmethod
    def set_current_path(new_path: Optional[str]) -> None:
        """Sets new current path for scroll/scroll_menu"""
        ApplicationState.current_path = new_path
