import pytest
import json
from unittest.mock import patch, MagicMock
from src.ai.ExecGuardian import ExecGuardian
from src.Settings import Settings


@pytest.fixture
def mock_settings_guard_off():
    mock = MagicMock(spec=Settings)
    mock.get.side_effect = lambda key: {
        "llm_model": "gpt-4o-mini",
        "debug": "off",
        "guard": "off",
    }.get(key)
    return mock


@pytest.fixture
def mock_settings_guard_on():
    mock = MagicMock(spec=Settings)
    mock.get.side_effect = lambda key: {
        "llm_model": "gpt-4o-mini",
        "debug": "off",
        "guard": "on",
    }.get(key)
    return mock


@pytest.fixture
def mock_settings_guard_auto():
    mock = MagicMock(spec=Settings)
    mock.get.side_effect = lambda key: {
        "llm_model": "gpt-4o-mini",
        "debug": "off",
        "guard": "auto",
    }.get(key)
    return mock


def test_ExecGuardian_off(mock_settings_guard_off):
    guardian = ExecGuardian("api-key", mock_settings_guard_off)
    guardian.confirm_execution = MagicMock(return_value=False)
    assert guardian.is_allowed("rm -rf /") == True


def test_ExecGuardian_on(mock_settings_guard_on):
    guardian = ExecGuardian("api-key", mock_settings_guard_on)
    guardian.confirm_execution = MagicMock(return_value=False)
    assert guardian.is_allowed("rm -rf /") == False
    guardian.confirm_execution = MagicMock(return_value=True)
    assert guardian.is_allowed("rm -rf /") == True


def test_ExecGuardian_auto(mock_settings_guard_auto):
    with patch("src.ai.ExecGuardian.ExecGuardian.ask") as mock_ask:
        mock_ask.return_value = "SAFE"
        guardian = ExecGuardian("api-key", mock_settings_guard_auto)
        guardian.confirm_execution = MagicMock(return_value=False)
        assert guardian.is_allowed("rm -rf /") == True

        mock_ask.return_value = "rm -rf / is a destructive command"
        guardian.confirm_execution = MagicMock(return_value=False)
        assert guardian.is_allowed("rm -rf /") == False
        guardian.confirm_execution = MagicMock(return_value=True)
        assert guardian.is_allowed("rm -rf /") == True
