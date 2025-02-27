import pytest
from src.Settings import Settings
from unittest.mock import patch, MagicMock


def test_load_config():
    with patch("src.Settings.open") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"llm_model": "gpt-4o-mini"}'
        )
        settings = Settings()
        assert settings._config == {"llm_model": "gpt-4o-mini"}


def test_load_config_file_not_found():
    with patch("src.Settings.open") as mock_open:
        mock_open.side_effect = FileNotFoundError
        settings = Settings()
        assert settings._config == {"llm_model": "gpt-4o-mini"}


def test_save_config():
    with patch("src.Settings.open") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"llm_model": "gpt-4o-mini"}'
        )
        settings = Settings()

        with patch("src.Settings.json.dump") as mock_dump:
            settings.save_config()
            mock_dump.assert_called_once_with(
                settings._config,
                mock_open.return_value.__enter__.return_value,
                indent=4,
            )


def test_get():
    with patch("src.Settings.open") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"llm_model": "gpt-4o-mini"}'
        )
        settings = Settings()

        assert settings.get("llm_model") == "gpt-4o-mini"


def test_set():
    with patch("src.Settings.open") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"llm_model": "gpt-4o-mini"}'
        )
        settings = Settings()

        with patch("src.Settings.json.dump") as mock_dump:
            settings.set("llm_model", "gpt-4o-medium")
            assert settings._config == {"llm_model": "gpt-4o-medium"}
            mock_dump.assert_called_once_with(
                settings._config,
                mock_open.return_value.__enter__.return_value,
                indent=4,
            )
