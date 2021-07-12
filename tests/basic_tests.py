import pytest
import os, sys
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from src.application_entry import *

#Copied from documentation
@pytest.fixture(autouse = True, scope = "function")
def mock_input():
    pipe_input = create_pipe_input()
    try:
        with create_app_session(input=pipe_input, output=DummyOutput()):
            yield pipe_input
    finally:
        pipe_input.close()

def test_basic_input(mock_input):
    input.send_text("Hello world!")

    assert result == "Hello world!"

if name == "__main__":
    main()
