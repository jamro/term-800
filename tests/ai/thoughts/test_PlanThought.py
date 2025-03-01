from src.ai.thoughts.PlanThought import PlanThought
import pytest
from unittest.mock import MagicMock
from src.ai.Assistant import Assistant
from src.ai.ConvoHistory import ConvoHistory


@pytest.fixture
def assistant_mock():
    mock = MagicMock(spec=Assistant)
    mock.history = MagicMock(spec=ConvoHistory)
    return mock


def test_PlanThought_simple(assistant_mock):
    assistant_mock.ask.return_value = "Plan 216317"
    thought = PlanThought(assistant_mock)
    response = thought.execute({"query": "What is the capital of France?"})

    assert "What is the capital of France?" in assistant_mock.ask.call_args[0][0]
    assert assistant_mock.history.clean_text.call_count == 1


def test_PlanThought_full_config(assistant_mock):
    assistant_mock.ask.return_value = "Plan 216317"
    on_data_callback = MagicMock()
    thought = PlanThought(
        assistant_mock, model_name="test_model", on_data_callback=on_data_callback
    )
    response = thought.execute({"query": "What is the capital of France?"})

    assert assistant_mock.ask.call_args.kwargs["model_name"] == "test_model"
    assert assistant_mock.ask.call_args.kwargs["on_data_callback"] == on_data_callback

    on_data_callback.assert_any_call("\n")
