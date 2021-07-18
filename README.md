# ThoughtBox

## Welcome to thinking inside the box
Thinking outside the box can be exhausting.

It's time to go back to simple.

Free yourself from distractions with Thought Box, the minimalist thought journal and note-taking application.

## Installation

### Bash Script
```bash
./run.sh
```

### Virtualenv
```bash
python3 -m venv .venv
pip install -r requirements.txt
python3 src/application_entry.py
```
## Usage

This application turns your terminal into your very own **Thought Box**. There, the only limits on the notes you can take are your imagination and the ASCII character set.

By pressing `CTRL+K`, you can open a menu packed with minimalist functionality.
From there, you can choose to create a new note or continue working on a previous note.
The clean, functional design frees you from the clutter of other text editors
No more worrying about centering or choosing the "right" font - just write what comes to you.

## Features
- Navigate and view files and folders using an interactive scrollbar menu.
- Create, move, and delete notes and folders.
- Convert text to emoji. You can turn `:smile:` into 😀, `:eggplant:` into 🍆, and many more.
- On startup, resume editing the file you last saved.
- Open external URLS straight from the app.
- Control the program using either a point-and-click interface or keyboard shortcuts.

## Keyboard Shortcuts
- `CTRL+K` Open top toolbar
- `ESC` Focus cursor on text field
- `CTRL+N` Start new file
- `CTRL+S` Save current file
- `CTRL+O` Open existing note
- `CTRL+Q` Exit application
- `CTRL+A` Select everything
- `CTRL+Z` Undo
- `CTRL+E` Emojify - i.e., turn text like `:smile:` into :smile:
- `ALT+O` Open link under cursor

Built with Python [Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit), Thought Box contains both a point-and-click interface and comprehensive keyboard shortcuts for mouse-free navigation.

## Brought to you in part by Team Adaptable Antelopes

<a href="https://github.com/BoraxTheClean/adaptable-antelopes/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=BoraxTheClean/adaptable-antelopes" />
</a>

Made with [contributors-img](https://contrib.rocks).
