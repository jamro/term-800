import pytest
import json
from unittest.mock import patch, MagicMock
from src.ai.Assistant import Assistant
from src.shell.RemoteShell import RemoteShell


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


def test_Assistant_run_command_simple(mock_openai_chat_stream_with_function):
    with (
        patch("src.ai.Assistant.Conversation") as conversation_mock,
        patch("src.ai.Conversation.openai.OpenAI") as mock_openai,
    ):
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream_with_function
        )

        remote_shell_mock = MagicMock(spec=RemoteShell)
        remote_shell_mock.exec.return_value = "t800"
        assistant = Assistant(remote_shell_mock, "api_key")
        assistant.ask("Hello")

        assert remote_shell_mock.exec.call_args[0][0] == "whoami"
        chat_dump = json.dumps(mock_client_instance.chat.completions.create.call_args)
        assert "whoami\\nt800" in chat_dump


def test_Assistant_run_command_hooks(mock_openai_chat_stream_with_function):
    with (
        patch("src.ai.Assistant.Conversation") as conversation_mock,
        patch("src.ai.Conversation.openai.OpenAI") as mock_openai,
    ):
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream_with_function
        )

        remote_shell_mock = MagicMock(spec=RemoteShell)
        remote_shell_mock.exec.return_value = "t800"
        assistant = Assistant(remote_shell_mock, "api_key")
        on_log_stream_mock = MagicMock()
        assistant.on_log_stream(on_log_stream_mock)
        assistant.ask("Hello")

        log_stream = on_log_stream_mock.call_args_list[0][0][0]
        assert log_stream.command == "whoami"

        remote_shell_mock.exec.assert_called_once_with("whoami", log_stream=log_stream)


def test_Assistant_get_total_cost(mock_openai_chat_stream_with_function):
    with (
        patch("src.ai.Assistant.Conversation") as conversation_mock,
        patch("src.ai.Conversation.openai.OpenAI") as mock_openai,
    ):
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream_with_function
        )

        remote_shell_mock = MagicMock(spec=RemoteShell)
        remote_shell_mock.exec.return_value = "t800"
        assistant = Assistant(remote_shell_mock, "api_key")
        assistant.ask("Hello")

        cost = assistant.get_total_cost()

        assert cost > 0
        assert cost < 0.1
