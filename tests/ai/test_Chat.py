import pytest
from src.ai.Chat import Chat
from src.ai.Assistant import Assistant
from src.shell.RemoteShell import RemoteShell
from unittest.mock import MagicMock, patch


@pytest.fixture
def assistant_mock():
    mock = MagicMock(spec=Assistant)
    mock.get_total_cost.return_value = 0.1
    return mock


@pytest.fixture
def shell_mock():
    return MagicMock(spec=RemoteShell)


@pytest.fixture
def console_mock():
    return MagicMock()


@pytest.fixture
def chat(console_mock, shell_mock, assistant_mock):
    return Chat(console_mock, shell_mock, assistant_mock)


def test_Chat_bye(chat, console_mock):
    with patch("src.ai.Chat.Prompt.ask", return_value="/bye"):
        chat.run()
        console_mock.print.assert_called_with("[yellow]Hasta la vista![/yellow]")


def test_Chat_ask(chat, assistant_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["Hello", "/bye"]):
        chat.run()
        assistant_mock.ask.assert_called_with("Hello")


def test_Chat_print_exec_prompt(chat, console_mock, assistant_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["whoami", "/bye"]):
        chat.run()
        assistant_mock.on_exec_prompt("whoami")

        console_args = [call[0][0] for call in console_mock.print.call_args_list]
        assert any(
            "whoami" in arg for arg in console_args
        ), f"No call contained 'whoami'. Calls: {console_args}"


def test_Chat_print_exec_response(chat, console_mock, assistant_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["whoami", "/bye"]):
        chat.run()
        assistant_mock.on_exec_response("root-user")

        console_args = [call[0][0] for call in console_mock.print.call_args_list]
        assert any(
            "root-user" in arg for arg in console_args
        ), f"No call contained 'root-user'. Calls: {console_args}"

        assistant_mock.on_exec_response("root-user\nmulti-line\noutput\nand more")

        console_args = [call[0][0] for call in console_mock.print.call_args_list]
        assert any(
            "and more" not in arg for arg in console_args
        ), f"A call contained 'and more'. Calls: {console_args}"
