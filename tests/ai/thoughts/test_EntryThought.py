from src.ai.thoughts.EntryThought import EntryThought
import pytest

def test_EntryThought_prep_plan():
    thought = EntryThought()
    response = thought.execute({
        "query": "What is the capital of France?",
        "prepare_plan": True
    })

    assert response['next_node'] == "prepare_plan"
    assert response['query'] == "What is the capital of France?"
    
def test_EntryThought_skip_plan():
    thought = EntryThought()
    response = thought.execute({
        "query": "What is the capital of France?",
        "prepare_plan": False
    })

    assert response['next_node'] == "skip_plan"
    assert response['query'] == "What is the capital of France?"