import os
import pytest
from unittest.mock import patch, MagicMock
from src.main import ask_openai


@pytest.fixture
def mock_openai_response():
    """Fixture to simulate a valid OpenAI API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello, this is a test response!"
    return mock_response


def test_ask_openai_missing_api_key():
    """Test ask_openai when API key is missing."""
    with (
        patch("os.getenv", return_value=None),
        patch("src.main.console.print") as mock_print,
    ):
        result = ask_openai("Test prompt")
        mock_print.assert_called_with(
            "[bold red]Error:[/bold red] OPENAI_API_KEY not set in .env file",
            style="bold red",
        )
        assert result is None


def test_ask_openai_success(mock_openai_response):
    """Test ask_openai with a valid API key and mocked OpenAI response."""
    with (
        patch("os.getenv", return_value="fake-api-key"),
        patch("src.main.OpenAI") as mock_openai,
    ):

        # Configure mock to return our fake response
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value = mock_openai_response

        result = ask_openai("Test prompt")

        # Verify that the OpenAI client was used correctly
        mock_openai.assert_called_with(api_key="fake-api-key")
        mock_client.chat.completions.create.assert_called_with(
            model="gpt-4o-mini", messages=[{"role": "user", "content": "Test prompt"}]
        )

        # Check if function returned expected result
        assert result == "Hello, this is a test response!"
