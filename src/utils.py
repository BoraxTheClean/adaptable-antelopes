import os

from constants import NOTES_DIR


def display_path(path: str) -> str:
    """Replaces NOTES_DIR with 'Explorer'"""
    return path.replace(NOTES_DIR, "Explorer")


def get_unique_filename(path: str) -> str:
    """Get a unique filename for a given path."""
    map_of_all_filenames = {i: True for i in os.listdir(path)}
    default_filename = "Thought Box Note"

    suffix = 0
    candidate_file_name = default_filename
    while candidate_file_name in map_of_all_filenames:
        suffix += 1
        candidate_file_name = default_filename + " " + str(suffix)

    return candidate_file_name


print(get_unique_filename(".thought_box"))
