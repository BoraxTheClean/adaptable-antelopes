# ThoughtBox

## Welcome to thinking inside the box
Thinking outside the box can be exhausting.

It's time to go back to simple.

Free yourself from distractions with Thought Box, our minimalist's thought journal and note-taking application.

## Usage

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
## How it works

Running this program will turn your terminal into your very own **Thought Box**. There, the only limits on the notes you can take are your imagination and the ASCII character set.

Built with Python [Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit), Thought Box contains both a point-and-click interface and comprehensive keyboard shortcuts for mouse-free navigation.

By pressing `CTRL+K`, you can open a menu packed with  minimalist functionality.

No more worrying about centering or choosing the 'right' font!

You can  choose to create a new note or continue working on a previous note.

## Features
- Scroll through files and folders under the `File` menu item.
- Convert text to emoji using the scroll bar in "Edit". Convert text such as `:smile:` to 😀, or `:eggplant:` to 🍆. Use `CTRL-E` to convert text to emoji.
- On startup, resume editing the file you last saved.
- Open an external URL straight from the app.

## Keyboard Shortcuts
- `CTRL+K` Open Top Tool Bar
- `ESC` Focus cursor on the text field
- `CTRL+N` Start a new file
- `CTRL+S` Save current file
- `CTRL+O` Open an existing note
- `CTRL+Q` Exit the application
- `CTRL+A` Select Everything
- `CTRL+Z` Undo
- `CTRL+E` Turn text like `:smile:` into :smile:
- `ALT+O` Open link under cursor


## Brought to you in part by Team Adaptable Antelopes

<a href="https://github.com/BoraxTheClean/adaptable-antelopes/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=BoraxTheClean/adaptable-antelopes" />
</a>

Made with [contributors-img](https://contrib.rocks).
