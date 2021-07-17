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


def get_dynamic_filename(directory: str, generic: str) -> str:
    """Determines the next in the sequence of dynamic filenames

    to use for a file not yet saved to a path by the user.
    The sequence goes 'Thought Box Note', 'Thought Box Note - 1',
    'Thought Box Note - 2',...
    """
    if not os.path.exists(zeroth := os.path.join(directory, generic + ".txt")):
        return zeroth
    elif not os.path.exists(
        first := os.path.join(directory, generic + " - 1" + ".txt")
    ):
        return first
    # If Thought Box Note - 1 exists, find highest n of Thought Box Notes - n
    # and return Thought Box Note - n + 1
    else:
        files = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        files = [
            os.path.splitext(f)[0]
            for f in files
            if generic + " - " in f and os.path.splitext(f)[0][-1].isdigit()
        ]
        latest_n = int(sorted(files)[-1][-1])
        return os.path.join(directory, generic + " - " + str(latest_n + 1) + ".txt")
