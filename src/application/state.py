class ApplicationState:
    """
    Application state.

    For the simplicity, we store this as a global, but better would be to
    instantiate this as an object and pass at around.
    """

    def __init__(self):
        self.show_status_bar = True
        self.current_path = None
