from constants import NOTES_DIR


def display_path(path: str) -> str:
    """Replaces NOTES_DIR with 'Explorer'"""
    return path.replace(NOTES_DIR, "Explorer")
