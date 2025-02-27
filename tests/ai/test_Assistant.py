import pytest
import json
from unittest.mock import patch, MagicMock
from src.ai.Assistant import Assistant
from src.shell.RemoteShell import RemoteShell


@pytest.fixture
def mock_openai_chat_stream(*args, **kwargs):
    responses = [
        {"choices": [MagicMock(delta=MagicMock(content="Hello", function_call=None))]},
        {"choices": [MagicMock(delta=MagicMock(content=None, function_call=None))]},
    ]

    def generator():
        for chunk in responses:
            yield MagicMock(**chunk)

    return generator()

@pytest.fixture
def mock_settings():
    mock = MagicMock()
    mock.get.side_effect = lambda key: {"llm_model": "gpt-4o-mini", "debug": "off"}.get(key)
    return mock


@pytest.fixture
def mock_openai_chat_stream_with_function(*args, **kwargs):
    func_chunk = MagicMock(arguments='{"command": "whoami"}')
    func_chunk.name = "run_shell_command"
    responses = [
        {
            "choices": [
                MagicMock(delta=MagicMock(content=None, function_call=func_chunk))
            ]
        },
        {"choices": [MagicMock(delta=MagicMock(content=None, function_call=None))]},
    ]

    def generator():
        for chunk in responses:
            yield MagicMock(**chunk)

    return generator()


@pytest.fixture
def mock_remote_shell():
    mock = MagicMock(spec=RemoteShell)
    mock.exec.return_value = "t800"
    mock.get_host_info.return_value = "host_info"
    mock.host = "skynet-2323.local"
    mock.user = "johnconnor"

    return mock


def test_Assistant_run_command_simple(
    mock_openai_chat_stream_with_function, mock_remote_shell, mock_settings
):
    with (
        patch("src.ai.Assistant.Conversation") as conversation_mock,
        patch("src.ai.Conversation.openai.OpenAI") as mock_openai,
    ):
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream_with_function
        )
        assistant = Assistant(mock_remote_shell, mock_settings, "api_key")
        assistant.ask("Hello")

        assert mock_remote_shell.exec.call_args[0][0] == "whoami"
        chat_dump = json.dumps(
            mock_client_instance.chat.completions.create.call_args, indent=2
        )
        assert "whoami" in chat_dump
        assert "t800" in chat_dump


def test_Assistant_run_command_hooks(
    mock_openai_chat_stream_with_function, mock_remote_shell, mock_settings
):
    with (
        patch("src.ai.Assistant.Conversation") as conversation_mock,
        patch("src.ai.Conversation.openai.OpenAI") as mock_openai,
    ):
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream_with_function
        )

        assistant = Assistant(mock_remote_shell, mock_settings, "api_key")
        on_log_stream_mock = MagicMock()
        assistant.on_log_stream(on_log_stream_mock)
        assistant.ask("Hello")

        log_stream = on_log_stream_mock.call_args_list[0][0][0]
        assert log_stream.command == "whoami"

        mock_remote_shell.exec.assert_called_once_with("whoami", log_stream=log_stream)


def test_Assistant_get_total_cost(
    mock_openai_chat_stream_with_function, mock_remote_shell, mock_settings
):
    with (
        patch("src.ai.Assistant.Conversation") as conversation_mock,
        patch("src.ai.Conversation.openai.OpenAI") as mock_openai,
    ):
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream_with_function
        )

        assistant = Assistant(mock_remote_shell, mock_settings, "api_key")
        assistant.ask("Hello")

        cost = assistant.get_total_cost()

        assert cost > 0
        assert cost < 0.1


def test_Assistant_summarise_long_stdout(
    mock_openai_chat_stream_with_function, mock_remote_shell, mock_settings
):
    with (
        patch("src.ai.Assistant.Conversation") as conversation_mock,
        patch("src.ai.Conversation.openai.OpenAI") as mock_openai,
        patch("src.ai.Assistant.Conversation") as conversation_mock,
    ):
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream_with_function
        )

        on_summary_start_mock = MagicMock()
        on_summary_end_mock = MagicMock()

        mock_remote_shell.exec.return_value = "a" * 10000
        conversation_mock.return_value.ask.return_value = "a_summary"
        assistant = Assistant(mock_remote_shell, mock_settings, "api_key")
        assistant.on_output_summary_start(on_summary_start_mock)
        assistant.on_output_summary_end(on_summary_end_mock)
        assistant.ask("Hello")

        assert mock_remote_shell.exec.call_args[0][0] == "whoami"
        chat_dump = json.dumps(mock_client_instance.chat.completions.create.call_args)
        assert "a_summary" in chat_dump

        on_summary_start_mock.assert_called_once()
        on_summary_end_mock.assert_called_once()


def test_Assistant_connect_ok(mock_remote_shell, mock_settings):
    with patch("src.ai.Assistant.Conversation") as conversation_mock:
        mock_remote_shell.get_host_info.return_value = "host_info5234523"
        assistant = Assistant(mock_remote_shell, mock_settings, "api_key")
        assistant.connect("host5", "user3")

        history_dump = assistant.history.dump()
        assert "host_info5234523" in history_dump
        assert "You are system admin" in history_dump

        assert mock_remote_shell.connect.call_args[0][0] == "host5"
        assert mock_remote_shell.connect.call_args[0][1] == "user3"


def test_Assistant_connect_fail(mock_remote_shell, mock_settings):
    with patch("src.ai.Assistant.Conversation") as conversation_mock:
        mock_remote_shell.connect.return_value = False
        assistant = Assistant(mock_remote_shell, mock_settings, "api_key")
        assert not assistant.connect("host5", "user3")


def test_Assistant_close(mock_remote_shell, mock_settings):
    with patch("src.ai.Assistant.Conversation") as conversation_mock:
        assistant = Assistant(mock_remote_shell, mock_settings, "api_key")
        assistant.close()
        mock_remote_shell.close.assert_called_once()

def test_ask(mock_remote_shell, mock_settings, mock_openai_chat_stream):
    with (
        patch("src.ai.Conversation.openai.OpenAI") as mock_openai,
        patch("builtins.print") as mock_print,
    ):
        mock_settings.get.side_effect = lambda key: {"llm_model": "gpt-4o-mini", "debug": "on"}.get(key)
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream
        )
        conversation = Assistant(mock_remote_shell, mock_settings, "api_key")
        assert conversation.ask("Hello") == "Hello"
        mock_print.assert_called_once()
        assert "Hello" in mock_print.call_args[0][0]

