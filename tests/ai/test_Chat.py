import pytest
from src.ai.Chat import Chat
from src.ai.Assistant import Assistant
from src.shell.LogStream import LogStream
from unittest.mock import MagicMock, patch


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
    return Chat(console_mock, assistant_mock)


def test_Chat_bye(chat, console_mock):
    with patch("src.ai.Chat.Prompt.ask", return_value="/bye"):
        chat.run()
        print(console_mock.print.call_args_list)
        console_mock.print.assert_called_with("[yellow]Hasta la vista![/yellow]")

def test_Chat_help(chat, console_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["/help", "/bye"]):
        chat.run()

        console_dump = "\n".join([call[0][0] for call in console_mock.print.call_args_list])
        assert "/help" in console_dump
        assert "/bye" in console_dump

def test_Chat_unknown_cmd(chat, console_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["/unknown", "/bye"]):
        chat.run()
        console_dump = "\n".join([call[0][0] for call in console_mock.print.call_args_list])
        assert "Command not found: 'unknown'" in console_dump

def test_Chat_ask(chat, assistant_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["Hello", "/bye"]):
        chat.run()
        assistant_mock.ask.assert_called()
        assert assistant_mock.ask.call_args[0][0] == "Hello"


def test_Chat_print_exec_prompt(chat, console_mock, assistant_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["whoami 23r4891", "/bye"]):
        chat.run()

        console_args = []
        for call in console_mock.print.call_args_list:
            if len(call) > 0 and len(call[0]) > 0:
                console_args.append(call[0][0])
        assert any(
            "whoami 23r4891" in arg for arg in console_args
        ), f"No call contained 'whoami'. Calls: {console_args}"


def test_Chat_print_exec_response(chat, assistant_mock):
    with (
        patch("src.ai.Chat.Prompt.ask", side_effect=["whoami", "/bye"]),
        patch("src.ai.Chat.Live") as live_mock,
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
        patch("src.ai.Chat.Prompt.ask", side_effect=["whoami", "/bye"]),
        patch("src.ai.Chat.Live") as live_mock,
    ):
        log_stream_mock = MagicMock(spec=LogStream)
        log_stream_mock.command = "whoami"
        chat.run()
        assistant_mock.on_log_stream.call_args[0][0](log_stream_mock)
        log_stream_mock.on_log.call_args[0][0]("line1")
        log_stream_mock.on_log.call_args[0][0]("line1")
        log_stream_mock.on_log.call_args[0][0]("line2")
        log_stream_mock.on_log.call_args[0][0]("line1")
        log_stream_mock.on_complete.call_args[0][0]()

        live_instance = live_mock.return_value

        assert (
            live_instance.update.call_args_list[-1][0][0].renderable
            == "[dim]line1\nline2\nline1[/dim]"
        )


def test_Chat_print_exec_response_keep_short(chat, assistant_mock):
    with (
        patch("src.ai.Chat.Prompt.ask", side_effect=["whoami", "/bye"]),
        patch("src.ai.Chat.Live") as live_mock,
    ):
        log_stream_mock = MagicMock(spec=LogStream)
        log_stream_mock.command = "whoami"
        chat.run()
        assistant_mock.on_log_stream.call_args[0][0](log_stream_mock)
        log_stream_mock.on_log.call_args[0][0]("line1")
        log_stream_mock.on_log.call_args[0][0]("line1")
        log_stream_mock.on_log.call_args[0][0]("line2")
        log_stream_mock.on_log.call_args[0][0]("line3")
        log_stream_mock.on_log.call_args[0][0]("line4")
        log_stream_mock.on_log.call_args[0][0]("line5")
        log_stream_mock.on_log.call_args[0][0]("line6")
        log_stream_mock.on_complete.call_args[0][0]()

        live_instance = live_mock.return_value

        assert (
            live_instance.update.call_args_list[-1][0][0].renderable
            == "[dim]...\nline2\nline3\nline4\nline5\nline6[/dim]"
        )


def test_Chat_welcome(chat, console_mock):
    chat.welcome(delay=0)

    output = "\n".join([call[0][0] for call in console_mock.print.call_args_list])
    print(output)

    assert "TERM-800 SYSTEM ADMINISTRATOR ONLINE" in output


def test_Chat_connect_ok(chat, console_mock, assistant_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["host212", "user847"]):
        chat.connect(delay=0)
        assistant_mock.connect.assert_called_with("host212", "user847")
        console_mock.print.assert_called_with("[yellow]Connected![/yellow]\n")


def test_Chat_connect_fail(chat, console_mock, assistant_mock):
    with patch("src.ai.Chat.Prompt.ask", side_effect=["host212", "user847"]):
        assistant_mock.connect.return_value = False
        chat.connect(delay=0)
        console_mock.print.assert_called_with(
            "[red][bold]Error: Connection timeout. Target unresponsive.[/bold][/red]"
        )
        assistant_mock.connect.assert_called_with("host212", "user847")
