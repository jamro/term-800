import pytest
from pyee import EventEmitter
from src.shell.LogStream import LogStream


def test_logstream_write_emits_log_event():
    log_stream = LogStream("test_command")
    log_lines = []

    def log_handler(line):
        log_lines.append(line)

    log_stream.on_log(log_handler)
    log_stream.write("line1\nline2\nline3")

    assert log_lines == ["line1", "line2", "line3"]


def test_logstream_done_emits_complete_event():
    log_stream = LogStream("test_command")
    complete_called = False

    def complete_handler():
        nonlocal complete_called
        complete_called = True

    log_stream.on_complete(complete_handler)
    log_stream.done()

    assert complete_called


def test_logstream_command_initialization():
    command = "test_command"
    log_stream = LogStream(command)
    assert log_stream.command == command


def test_logstream_emitter_initialization():
    log_stream = LogStream("test_command")
    assert isinstance(log_stream.emitter, EventEmitter)
