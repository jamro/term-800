import pytest
from unittest.mock import patch, MagicMock

"""
List of tests for RemoteShell class
- test_init
- test_test_connection
- test_exec
"""


def test_init():
    with patch("src.shell.RemoteShell.Connection"):
        from src.shell.RemoteShell import RemoteShell

        rs = RemoteShell("localhost", "user")
        assert rs.host == "localhost"
        assert rs.user == "user"


def test_test_connection_ok():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:
        from src.shell.RemoteShell import RemoteShell

        rs = RemoteShell("localhost", "user")
        result = rs.test_connection()
        mock_conn.assert_called_once_with(host="localhost", user="user")
        mock_conn.return_value.open.assert_called_once()


def test_test_connection_fail():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:
        from src.shell.RemoteShell import RemoteShell

        rs = RemoteShell("localhost", "user")
        mock_conn.return_value.open.side_effect = Exception("Connection failed")
        result = rs.test_connection()
        mock_conn.assert_called_once_with(host="localhost", user="user")
        mock_conn.return_value.open.assert_called_once()
        assert result == False


def test_exec_ok():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:
        from src.shell.RemoteShell import RemoteShell

        rs = RemoteShell("localhost", "user")
        mock_conn.return_value.run.return_value.stdout = "Hello"
        mock_conn.return_value.run.return_value.stderr = ""
        mock_conn.return_value.run.return_value.failed = False
        mock_conn.return_value.run.return_value.exited = 0
        result = rs.exec("echo Hello")
        mock_conn.assert_called_once_with(host="localhost", user="user")
        mock_conn.return_value.run.assert_called_once_with(
            "echo Hello", hide=True, warn=True
        )
        assert result == "Hello"


def test_exec_fail():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:
        from src.shell.RemoteShell import RemoteShell

        rs = RemoteShell("localhost", "user")
        mock_conn.return_value.run.return_value.stdout = "Hello"
        mock_conn.return_value.run.return_value.stderr = "Error"
        mock_conn.return_value.run.return_value.failed = True
        mock_conn.return_value.run.return_value.exited = 1
        result = rs.exec("echo Hello")
        mock_conn.assert_called_once_with(host="localhost", user="user")
        mock_conn.return_value.run.assert_called_once_with(
            "echo Hello", hide=True, warn=True
        )
        assert result == "Hello\nError: Error\nExit Code: 1"
