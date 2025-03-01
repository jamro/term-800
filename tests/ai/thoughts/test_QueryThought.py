from src.ai.thoughts.QueryThought import QueryThought
import pytest
from unittest.mock import MagicMock
from src.ai.Assistant import Assistant
from src.ai.ConvoHistory import ConvoHistory

@pytest.fixture
def assistant_mock():
    mock = MagicMock(spec=Assistant)
    mock.history = MagicMock(spec=ConvoHistory)
    return mock

def test_QueryThought_simple(assistant_mock):
    assistant_mock.ask.return_value = "answer2347892"
    thought = QueryThought(assistant_mock, post_exec_prompt="post_exec_prompt_324")
    response = thought.execute({
        "query": "What is the capital of France?"
    })

    assert response["response"] == "answer2347892"
    assistant_mock.history.clean_text.assert_called_with("post_exec_prompt_324")
