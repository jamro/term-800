import pytest
from unittest.mock import patch, MagicMock
from src.ai.ThoughtNode import ThoughtNode


def test_ThoughtNode_func_thought():
    thought = MagicMock()
    node = ThoughtNode(thought=thought)
    node.execute("intput2134")
    thought.assert_called_once_with("intput2134")


def test_ThoughtNode_str_thought():
    thought = "test"
    node = ThoughtNode(thought=thought)
    assert node.execute() == thought


def test_THoughtNode_no_thought():
    node = ThoughtNode()
    assert node.execute() == None


def test_ChainOfThoughts_flow_simple():

    node1 = ThoughtNode(thought=lambda input: input + "X")
    node2 = ThoughtNode(thought=lambda input: input + "A")
    node3 = ThoughtNode(thought=lambda input: input + "B")

    node1.connect(node2, lambda x: x == "XX")
    node1.connect(node3, lambda x: x == "YX")

    assert node1.execute("X") == "XXA"
    assert node1.execute("Y") == "YXB"
    assert node1.execute("Z") == "ZX"
