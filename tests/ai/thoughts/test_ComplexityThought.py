from src.ai.thoughts.ComplexityThought import ComplexityThought
import pytest
from unittest.mock import MagicMock
from src.ai.Assistant import Assistant
from src.ai.ConvoHistory import ConvoHistory

@pytest.fixture
def assistant_mock():
    mock = MagicMock(spec=Assistant)
    mock.history = MagicMock(spec=ConvoHistory)
    return mock

def test_ComplexityThought_simple(assistant_mock):
    assistant_mock.ask.return_value = "SIMPLE"
    thought = ComplexityThought(assistant_mock)
    response = thought.execute({
        "query": "What is the capital of France?"
    })

    assert response['complexity'] == "SIMPLE"
    assert response['query'] == "What is the capital of France?"
    

def test_ComplexityThought_complex(assistant_mock):
    assistant_mock.ask.return_value = "COMPLEX"
    thought = ComplexityThought(assistant_mock)
    response = thought.execute({
        "query": "What is the capital of France?"
    })

    assert response['complexity'] == "COMPLEX"
    assert response['query'] == "What is the capital of France?"


def test_ComplexityThought_full_config(assistant_mock):
    assistant_mock.ask.return_value = "SIMPLE"
    thought = ComplexityThought(assistant_mock, model_name="test_model")
    response = thought.execute({
        "query": "What is the capital of France?"
    })

    assert assistant_mock.ask.call_args.kwargs['model_name'] == "test_model"
