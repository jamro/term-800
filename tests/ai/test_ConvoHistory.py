import pytest
from src.ai.ConvoHistory import ConvoHistory


def test_ConvoHistory_init():
    convo = ConvoHistory()
    assert len(convo.get_items()) == 1
    assert convo.get_items()[0]["role"] == "system"
    assert convo.get_system_message() == ""


def test_ConvoHistory_set_system_message():
    convo = ConvoHistory()
    convo.set_system_message("Hello")
    assert convo.get_system_message() == "Hello"
    assert convo.get_items()[0]["content"] == "Hello"

    convo.set_system_message("World")
    assert convo.get_system_message() == "World"
    assert convo.get_items()[0]["content"] == "World"


def test_ConvoHistory_append_message():
    convo = ConvoHistory()
    convo.append_message("user", "Hello")
    assert len(convo.get_items()) == 2
    assert convo.get_items()[1]["role"] == "user"
    assert convo.get_items()[1]["content"] == "Hello"


def test_ConvoHistory_dump():
    convo = ConvoHistory()
    convo.append_message("user", "Hello1876")
    convo.set_system_message("World289716")
    dump = convo.dump()
    assert "Hello1876" in dump
    assert "World289716" in dump
    assert "user" in dump
    assert "system" in dump


def test_ConvoHistory_clean_text():
    convo = ConvoHistory()
    convo.set_system_message("SysRockMsg")
    convo.append_message("user", "HelloRock1876")
    convo.append_message("user", "Ro.ck\nRock\nROCK")
    convo.clean_text("Rock")
    assert convo.get_items()[0]["content"] == "SysRockMsg"
    assert convo.get_items()[1]["content"] == "Hello1876"
    assert convo.get_items()[2]["content"] == "Ro.ck\n\nROCK"


def test_ConvoHistory_clean_transformed():
    convo = ConvoHistory()
    convo.set_system_message("SysRockMsg")
    convo.append_message("user", "HelloRock1876")
    convo.append_message("user", "Ro.ck\nRock\nROCK")
    convo.clean_transformed(lambda x: x.replace("Rock", "ABC"))
    assert convo.get_items()[0]["content"] == "SysRockMsg"
    assert convo.get_items()[1]["content"] == "HelloABC1876"
    assert convo.get_items()[2]["content"] == "Ro.ck\nABC\nROCK"


def test_ConvoHistory_clear():
    convo = ConvoHistory()
    convo.set_system_message("Sys73269")
    convo.append_message("user", "HelloRock1876")
    convo.clear()
    assert len(convo.get_items()) == 1
    assert convo.get_system_message() == "Sys73269"


def test_Convo_undo():
    convo = ConvoHistory()
    convo.append_message("user", "msg1")
    convo.append_message("user", "msg2")
    convo.append_message("user", "msg3")
    convo.undo(2)
    assert len(convo.get_items()) == 2
    assert convo.get_items()[0]["role"] == "system"
    assert convo.get_items()[-1]["content"] == "msg1"

    convo.undo()
    assert len(convo.get_items()) == 1
    assert convo.get_items()[0]["role"] == "system"
