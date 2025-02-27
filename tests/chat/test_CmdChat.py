import pytest
from src.chat.CmdChat import CmdChat
from src.ai.Assistant import Assistant
from src.shell.LogStream import LogStream
from unittest.mock import MagicMock, patch
import json


@pytest.fixture
def assistant_mock():
    mock = MagicMock(spec=Assistant)
    mock.get_total_cost.return_value = 0.1
    return mock


@pytest.fixture
def console_mock():
    return MagicMock()


@pytest.fixture
def chat(console_mock, assistant_mock):
    return CmdChat(console_mock, assistant_mock)


def test_CmdChat_bye(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", return_value="/bye"):
        chat.run()
        print(console_mock.print.call_args_list)
        console_mock.print.assert_called_with("[yellow]Hasta la vista![/yellow]")

def test_CmdChat_help(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["/help", "/bye"]):
        chat.run()

        console_dump = json.dumps(
            [call for call in console_mock.print.call_args_list]
        )
        assert "/help" in console_dump
        assert "/bye" in console_dump

def test_CmdChat_unknown_cmd(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["/unknown", "/bye"]):
        chat.run()
        console_dump = "\n".join([call[0][0] for call in console_mock.print.call_args_list])
        assert "Command not found: 'unknown'" in console_dump

def test_CmdChat_ask(chat, assistant_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["Hello", "/bye"]):
        chat.run()
        assistant_mock.ask.assert_called()
        assert assistant_mock.ask.call_args[0][0] == "Hello"

