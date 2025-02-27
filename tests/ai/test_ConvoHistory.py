import pytest
from src.ai.ConvoHistory import ConvoHistory


def test_init():
    convo = ConvoHistory()
    assert len(convo.get_items()) == 1
    assert convo.get_items()[0]["role"] == "system"
    assert convo.get_system_message() == ""


def test_set_system_message():
    convo = ConvoHistory()
    convo.set_system_message("Hello")
    assert convo.get_system_message() == "Hello"
    assert convo.get_items()[0]["content"] == "Hello"

    convo.set_system_message("World")
    assert convo.get_system_message() == "World"
    assert convo.get_items()[0]["content"] == "World"


def test_append_message():
    convo = ConvoHistory()
    convo.append_message("user", "Hello")
    assert len(convo.get_items()) == 2
    assert convo.get_items()[1]["role"] == "user"
    assert convo.get_items()[1]["content"] == "Hello"


def test_dump():
    convo = ConvoHistory()
    convo.append_message("user", "Hello1876")
    convo.set_system_message("World289716")
    dump = convo.dump()
    assert "Hello1876" in dump
    assert "World289716" in dump
    assert "user" in dump
    assert "system" in dump
