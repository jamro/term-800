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


def test_ThoughtNode_flow():

    node1 = ThoughtNode(thought=lambda input: input + "X")
    node2 = ThoughtNode(thought=lambda input: input + "A")
    node3 = ThoughtNode(thought=lambda input: input + "B")

    node1.connect(node2, lambda x: x == "XX")
    node1.connect(node3, lambda x: x == "YX")

    assert node1.execute("X") == "XXA"
    assert node1.execute("Y") == "YXB"
    assert node1.execute("Z") == "ZX"


def test_ThoughtNode_log():

    class CustomNode(ThoughtNode):
        def __init__(self, thought=None):
            super().__init__(thought)

    node1 = ThoughtNode(thought=lambda input: input + "X")
    node2 = CustomNode(thought=lambda input: input + "A")
    node3 = ThoughtNode(thought=lambda input: input + "B")

    node1.connect(node2)
    node2.connect(node3)

    node1.execute("X")

    assert node1.log == [
        {
            "step": "ThoughtNode",
            "input": "X",
            "output": "XX",
        },
        {
            "step": "CustomNode",
            "input": "XX",
            "output": "XXA",
        },
        {
            "step": "ThoughtNode",
            "input": "XXA",
            "output": "XXAB",
        },
    ]
