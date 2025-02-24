from unittest.mock import patch, MagicMock
from src.ai.Conversation import Conversation
import pytest
import json


@pytest.fixture
def mock_openai_chat_stream(*args, **kwargs):
    responses = [
        {"choices": [MagicMock(delta=MagicMock(content="Hello", function_call=None))]},
        {"choices": []},
        {"choices": [MagicMock(delta=None)]},
        {"choices": [MagicMock(delta=MagicMock(content=", how", function_call=None))]},
        {
            "choices": [
                MagicMock(delta=MagicMock(content=" are you", function_call=None))
            ]
        },
        {"choices": [MagicMock(delta=MagicMock(content="?", function_call=None))]},
        {"choices": [MagicMock(delta=MagicMock(content=None, function_call=None))]},
    ]

    def generator():
        for chunk in responses:
            yield MagicMock(**chunk)

    return generator()


@pytest.fixture
def mock_openai_chat_stream_with_function(*args, **kwargs):
    func_chunk1 = MagicMock(arguments='{"arg1": "Hello", "a')
    func_chunk2 = MagicMock(arguments='rg2": "World"}')
    func_chunk1.name = "my_test_function"
    func_chunk2.name = "my_test_function"
    responses = [
        {"choices": [MagicMock(delta=MagicMock(content="Hello", function_call=None))]},
        {
            "choices": [
                MagicMock(delta=MagicMock(content=None, function_call=func_chunk1))
            ]
        },
        {
            "choices": [
                MagicMock(delta=MagicMock(content=None, function_call=func_chunk2))
            ]
        },
        {"choices": [MagicMock(delta=MagicMock(content=None, function_call=None))]},
    ]

    def generator():
        for chunk in responses:
            yield MagicMock(**chunk)

    return generator()


def test_init():
    conversation = Conversation("api_key")
    assert conversation.api_key == "api_key"
    assert conversation.model_name == "gpt-4o-mini"


def test_add_function():
    conversation = Conversation("api_key")
    conversation.add_function("name", "description", "logic", {"key": "value"})
    assert conversation.functions == [
        {
            "name": "name",
            "description": "description",
            "parameters": {"key": "value"},
            "logic": "logic",
        }
    ]


def test_get_models():
    with patch("src.ai.Conversation.openai.OpenAI") as mock_openai:
        mock_openai.return_value.models.list.return_value.data = [
            MagicMock(id="model-1"),
            MagicMock(id="model-2"),
        ]
        conversation = Conversation("api_key")
        assert conversation.get_models() == ["model-1", "model-2"]


def test_ask(mock_openai_chat_stream):
    with patch("src.ai.Conversation.openai.OpenAI") as mock_openai:
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream
        )
        conversation = Conversation("api_key")
        assert conversation.ask("Hello, how are you?") == "Hello, how are you?"


def test_ask_recursion_limit(mock_openai_chat_stream_with_function):
    with patch("src.ai.Conversation.openai.OpenAI") as mock_openai:
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream_with_function
        )
        test_logic = MagicMock(return_value="Test Resonse From Function")

        conversation = Conversation("api_key")
        conversation.add_function(
            "my_test_function",
            "test_description",
            logic=test_logic,
            parameters={
                "type": "object",
                "properties": {
                    "arg1": {"type": "string", "description": "arg1 description"},
                    "arg2": {"type": "string", "description": "arg2 description"},
                },
                "required": ["arg1", "arg2"],
            },
        )
        conversation.ask("Hello")
        test_logic.assert_called_once()

        history_dump = json.dumps(conversation.history)
        assert "Test Resonse From Function" in history_dump

        assert mock_client_instance.chat.completions.create.call_count == 2


def test_set_system_message():
    conversation = Conversation(
        "api_key", system_message="You are a test assistant 7362"
    )
    history_dump = json.dumps(conversation.history)
    assert "You are a test assistant 7362" in history_dump


def test_recursion_limit():
    conversation = Conversation("api_key")
    with pytest.raises(ValueError):
        conversation.ask("Hello", recurence_limit=0)


def test_on_data_callback(mock_openai_chat_stream):
    with patch("src.ai.Conversation.openai.OpenAI") as mock_openai:
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream
        )

        log = ""

        def on_data_callback(data):
            nonlocal log
            log += data

        conversation = Conversation("api_key")
        conversation.ask("Hello", on_data_callback=on_data_callback)
        assert log == "Hello, how are you?"


def test_Conversation_stats(mock_openai_chat_stream):
    with patch("src.ai.Conversation.openai.OpenAI") as mock_openai:
        mock_client_instance = mock_openai.return_value
        mock_client_instance.chat.completions.create.return_value = (
            mock_openai_chat_stream
        )
        conversation = Conversation("api_key")
        conversation.ask("Hello, how are you?", model_name="gpt-4o-mini")
        conversation.ask("Madagascar", model_name="gpt-4o")

        print(conversation.token_stats)

        assert conversation.token_stats == {
            "gpt-4o-mini": {
                "input_tokens": 18,
                "output_tokens": 6,
            },
            "gpt-4o": {
                "input_tokens": 50,
                "output_tokens": 0,
            }
        }