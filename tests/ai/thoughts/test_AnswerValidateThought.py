from src.ai.thoughts.AnswerValidateThought import AnswerValidateThought
import pytest
from unittest.mock import MagicMock
from src.ai.Assistant import Assistant
from src.ai.ConvoHistory import ConvoHistory


@pytest.fixture
def assistant_mock():
    mock = MagicMock(spec=Assistant)
    mock.history = MagicMock(spec=ConvoHistory)
    return mock


def test_AnswerValidateThought_completed(assistant_mock):
    assistant_mock.ask.return_value = "YES"
    thought = AnswerValidateThought(assistant_mock)
    response = thought.execute({"query": "What is the capital of France?"})

    assert response["next_node"] == "YES"
    assert response["query"] == "What is the capital of France?"


def test_AnswerValidateThought_followup(assistant_mock):
    assistant_mock.ask.return_value = "NEXT"
    thought = AnswerValidateThought(assistant_mock)
    response = thought.execute({"query": "What is the capital of France?"})

    assert response["next_node"] == "NEXT"
    assert response["query"] == "continue"


def test_AnswerValidateThought_full_config(assistant_mock):
    assistant_mock.ask.return_value = "YES"
    thought = AnswerValidateThought(assistant_mock, model_name="test_model")
    response = thought.execute(
        {"query": "What is the capital of France?", "next_node": "YES"}
    )

    assert assistant_mock.ask.call_args.kwargs["model_name"] == "test_model"
