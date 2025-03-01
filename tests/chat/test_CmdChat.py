import pytest
from src.chat.CmdChat import CmdChat
from src.ai.Assistant import Assistant
from src.ai.ConvoHistory import ConvoHistory
from src.ai.Conversation import Conversation
from src.Settings import Settings
from src.shell.RemoteShell import RemoteShell
from unittest.mock import MagicMock, patch
import json


@pytest.fixture
def mock_settings():
    mock = MagicMock(spec=Settings)
    mock.get.side_effect = lambda key: {"llm_model": "gpt-4o-mini"}.get(key)
    return mock


@pytest.fixture
def assistant_mock():
    mock = MagicMock(spec=Assistant)
    mock.api_key = "test_key_123"
    mock.history = MagicMock(spec=ConvoHistory)
    mock.shell = MagicMock(spec=RemoteShell)
    mock.shell.host = "test_host_937"
    mock.shell.user = "test_user_243"
    mock.model_name = "gpt-4o-mini"
    mock.history.get_items.return_value = [{"role": "system", "content": "Hello"}]
    mock.get_chain_of_thoughts_log.return_value = [
        {
            "step": "test_thought",
            "input": {
                "query": "Hello",
            },
            "output": {
                "query": "Hello",
                "answer": "Hi",
            },
        }
    ]
    mock.get_total_cost.return_value = 0.1
    return mock


@pytest.fixture
def console_mock():
    return MagicMock()


@pytest.fixture
def chat(console_mock, assistant_mock, mock_settings):
    return CmdChat(console_mock, mock_settings, assistant_mock)


def test_CmdChat_bye(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", return_value="/bye"):
        chat.run()
        print(console_mock.print.call_args_list)
        console_mock.print.assert_called_with("[yellow]Hasta la vista![/yellow]")


def test_CmdChat_help(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["/help", "/bye"]):
        chat.run()

        console_dump = json.dumps([call for call in console_mock.print.call_args_list])
        assert "/help" in console_dump
        assert "/bye" in console_dump
        assert "/model" in console_dump


def test_CmdChat_unknown_cmd(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["/unknown", "/bye"]):
        chat.run()
        console_dump = json.dumps([call for call in console_mock.print.call_args_list])
        assert "Command not found" in console_dump


def test_CmdChat_ask(chat, assistant_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["Hello", "/bye"]):
        chat.run()
        assistant_mock.think.assert_called()
        assert assistant_mock.think.call_args[0][0] == "Hello"


def test_CmdChat_model_unknwon(chat, console_mock):
    with (
        patch("src.chat.Chat.Prompt.ask", side_effect=["/model gpt-unknwon", "/bye"]),
        patch("src.chat.CmdChat.Conversation", return_value=MagicMock(spec=Conversation)) as mock_convo,
    ):
        convo_instance = mock_convo.return_value
        convo_instance.ask.side_effect = Exception("Error")
        chat.run()
        console_dump = json.dumps([call for call in console_mock.print.call_args_list])
        assert "Unsupported language model" in console_dump


def test_CmdChat_model_basic(chat, console_mock, mock_settings):
    with (
      patch("src.chat.Chat.Prompt.ask", side_effect=["/model gpt-4o", "/bye"]),
      patch("src.chat.CmdChat.Conversation", return_value=MagicMock(spec=Conversation)) as mock_convo,
    ):
        convo_instance = mock_convo.return_value
        convo_instance.ask.return_value = "OK"
        chat.run()
        console_dump = json.dumps([call for call in console_mock.print.call_args_list])
        assert "Language model changed to 'gpt-4o'" in console_dump
        assert chat.assistant.model_name == "gpt-4o"
        mock_settings.set.assert_called_with("llm_model", "gpt-4o")


def test_CmdChat_model_missing_arg(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["/model", "/bye"]):
        chat.run()
        console_dump = json.dumps([call for call in console_mock.print.call_args_list])
        assert f"Current LLM model: [bold]{chat.assistant.model_name}[/bold]" in console_dump


def test_CmdChat_debug(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["/debug", "/bye"]):
        chat.run()
        console_dump = json.dumps([call for call in console_mock.print.call_args_list])
        assert "----- CONVERSATION HISTORY -----" in console_dump


def test_CmdChat_clear(chat, console_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["/clear", "/bye"]):
        chat.run()
        chat.assistant.history.clear.assert_called()
