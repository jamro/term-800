import pytest
from src.chat.Chat import Chat
from src.ai.Assistant import Assistant
from src.shell.LogStream import LogStream
from src.Settings import Settings
from unittest.mock import MagicMock, patch
import json
from src.shell.RemoteShell import RemoteShell
from src.ai.ExecGuardian import ExecGuardian


@pytest.fixture
def mock_settings():
    mock = MagicMock(spec=Settings)
    mock.get.side_effect = lambda key: {"llm_model": "gpt-4o-mini"}.get(key)
    mock.set.side_effect = lambda key, value: None
    return mock


@pytest.fixture
def assistant_mock():
    mock = MagicMock(spec=Assistant)
    mock.get_total_cost.return_value = 0.1
    mock.shell = MagicMock(spec=RemoteShell)
    mock.shell.host = "test_host_937"
    mock.shell.user = "test_user_243"
    mock.model_name = "gpt-4o-mini"
    mock.guardian = MagicMock(spec=ExecGuardian)
    mock.guardian.confirm_execution = lambda: True
    mock.connect.return_value = "OK"
    return mock


@pytest.fixture
def console_mock():
    return MagicMock()


@pytest.fixture
def chat(console_mock, assistant_mock, mock_settings):
    return Chat(console_mock, mock_settings, assistant_mock)


def test_Chat_ask(chat, assistant_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["Hello", "/bye"]):
        chat.run()
        assistant_mock.think.assert_called()
        assert assistant_mock.think.call_args[0][0] == "Hello"


def test_Chat_print_exec_response(chat, assistant_mock):
    with (
        patch("src.chat.Chat.Prompt.ask", side_effect=["whoami", "/bye"]),
        patch("src.chat.Chat.Live") as live_mock,
    ):
        log_stream_mock = MagicMock(spec=LogStream)
        log_stream_mock.command = "whoami"
        chat.run()
        assistant_mock.on_log_stream.call_args[0][0](log_stream_mock)
        log_stream_mock.on_log.call_args[0][0](
            "root-user\nmulti-line\noutput\nand more"
        )
        log_stream_mock.on_complete.call_args[0][0]()

        live_instance = live_mock.return_value

        live_instance.start.assert_called()
        live_instance.stop.assert_called()

        console_args = [
            call[0][0].renderable for call in live_instance.update.call_args_list
        ]
        assert any(
            "root-user" in arg for arg in console_args
        ), f"No call contained 'root-user'. Calls: {console_args}"


def test_Chat_print_exec_response_skip_duplicates(chat, assistant_mock):
    with (
        patch("src.chat.Chat.Prompt.ask", side_effect=["whoami", "/bye"]),
        patch("src.chat.Chat.Live") as live_mock,
    ):
        log_stream_mock = MagicMock(spec=LogStream)
        log_stream_mock.command = "whoami"
        chat.run()
        assistant_mock.on_log_stream.call_args[0][0](log_stream_mock)
        log_stream_mock.on_log.call_args[0][0]("line1\n")
        log_stream_mock.on_log.call_args[0][0]("line1\n")
        log_stream_mock.on_log.call_args[0][0]("line2\n")
        log_stream_mock.on_log.call_args[0][0]("line1\n")
        log_stream_mock.on_complete.call_args[0][0]()

        live_instance = live_mock.return_value

        assert (
            live_instance.update.call_args_list[-1][0][0].renderable
            == "[dim]line1\nline2\nline1[/dim]"
        )


def test_Chat_print_exec_response_carriage_return(chat, assistant_mock):
    with (
        patch("src.chat.Chat.Prompt.ask", side_effect=["whoami", "/bye"]),
        patch("src.chat.Chat.Live") as live_mock,
    ):
        log_stream_mock = MagicMock(spec=LogStream)
        log_stream_mock.command = "whoami"
        chat.run()
        assistant_mock.on_log_stream.call_args[0][0](log_stream_mock)
        log_stream_mock.on_log.call_args[0][0]("line1\n")
        log_stream_mock.on_log.call_args[0][0]("line2\n")
        log_stream_mock.on_log.call_args[0][0]("line3\r")
        log_stream_mock.on_log.call_args[0][0]("line4\n")
        log_stream_mock.on_complete.call_args[0][0]()

        live_instance = live_mock.return_value

        assert (
            live_instance.update.call_args_list[-1][0][0].renderable
            == "[dim]line1\nline2\nline4[/dim]"
        )


def test_Chat_print_exec_response_keep_short(chat, assistant_mock):
    with (
        patch("src.chat.Chat.Prompt.ask", side_effect=["whoami", "/bye"]),
        patch("src.chat.Chat.Live") as live_mock,
    ):
        log_stream_mock = MagicMock(spec=LogStream)
        log_stream_mock.command = "whoami"
        chat.run()
        assistant_mock.on_log_stream.call_args[0][0](log_stream_mock)
        log_stream_mock.on_log.call_args[0][0]("line1\n")
        log_stream_mock.on_log.call_args[0][0]("line1\n")
        log_stream_mock.on_log.call_args[0][0]("line2\n")
        log_stream_mock.on_log.call_args[0][0]("line3\n")
        log_stream_mock.on_log.call_args[0][0]("line4\n")
        log_stream_mock.on_log.call_args[0][0]("line5\n")
        log_stream_mock.on_log.call_args[0][0]("line6\n")
        log_stream_mock.on_complete.call_args[0][0]()

        live_instance = live_mock.return_value

        assert (
            live_instance.update.call_args_list[-1][0][0].renderable
            == "[dim]...\nline3\nline4\nline5\nline6[/dim]"
        )


def test_Chat_welcome(chat, console_mock):
    chat.welcome(delay=0)

    output = "\n".join([call[0][0] for call in console_mock.print.call_args_list])
    print(output)

    assert "TERM-800 SYSTEM ADMINISTRATOR ONLINE" in output


def test_Chat_connect_ok(chat, console_mock, assistant_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["host212", "user847"]):
        chat.connect(delay=0)
        assistant_mock.connect.assert_called_with("host212", "user847")
        console_mock.print.assert_called_with("[yellow]Connected![/yellow]\n")


def test_Chat_connect_fail(chat, console_mock, assistant_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["host212", "user847"]):
        assistant_mock.connect.return_value = "ERROR: Connection timeout"
        chat.connect(delay=0)
        console_mock.print.assert_called_with(
            "[red][bold]ERROR: Connection timeout[/bold][/red]"
        )
        assistant_mock.connect.assert_called_with("host212", "user847")


def test_Chat_store_default_host_and_user(chat, mock_settings):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["host3", "user1"]):
        chat.connect(delay=0)

        mock_settings.set.assert_any_call("host", "host3")
        mock_settings.set.assert_any_call("user", "user1")


def test_Chat_ask_for_password(chat, console_mock, assistant_mock):
    with patch(
        "src.chat.Chat.Prompt.ask",
        side_effect=["host212", "user847", "wrong_pass", "password123"],
    ):
        assistant_mock.connect.side_effect = ["AUTH_ERROR", "AUTH_ERROR", "OK"]
        chat.connect(delay=0)
        assistant_mock.connect.assert_any_call("host212", "user847")
        assistant_mock.connect.assert_any_call("host212", "user847", "wrong_pass")
        assistant_mock.connect.assert_any_call("host212", "user847", "password123")
        console_mock.print.assert_called_with("[yellow]Connected![/yellow]\n")


def test_Chat_confirm_execution(chat, assistant_mock):
    with patch("src.chat.Chat.Prompt.ask", side_effect=["y", "n"]):
        assert (
            assistant_mock.guardian.confirm_execution("whoami", "details-27518") == True
        )
        assert (
            assistant_mock.guardian.confirm_execution("whoami", "details-27518")
            == False
        )

def test_Chat_handle_openai_errors(chat, assistant_mock, console_mock):
    with (
        patch("src.chat.Chat.Prompt.ask", side_effect=["Hello", "/bye"]),
    ):
        assistant_mock.think.side_effect = Exception("OpenAI API returned an error")
        chat.run()
        assistant_mock.think.assert_called()
        assert assistant_mock.think.call_args[0][0] == "Hello"

        console_dump = json.dumps([call for call in console_mock.print.call_args_list])
        assert "OpenAI API returned an error" in console_dump