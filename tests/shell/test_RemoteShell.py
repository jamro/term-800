import pytest
from unittest.mock import patch, MagicMock
from src.shell.RemoteShell import RemoteShell


def test_RemoteShell_init():
    with patch("src.shell.RemoteShell.Connection"):

        rs = RemoteShell("localhost", "user")
        assert rs.host == "localhost"
        assert rs.user == "user"


def test_RemoteShell_test_connection_ok():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell("localhost", "user")
        result = rs.test_connection()
        mock_conn.assert_called_once_with(host="localhost", user="user")
        mock_conn.return_value.open.assert_called_once()


def test_RemoteShell_test_connection_fail():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell("localhost", "user")
        mock_conn.return_value.open.side_effect = Exception("Connection failed")
        result = rs.test_connection()
        mock_conn.assert_called_once_with(host="localhost", user="user")
        mock_conn.return_value.open.assert_called_once()
        assert result == False


def test_RemoteShell_exec_ok():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell("localhost", "user")
        mock_conn.return_value.run.return_value.stdout = "Hello"
        mock_conn.return_value.run.return_value.stderr = ""
        mock_conn.return_value.run.return_value.failed = False
        mock_conn.return_value.run.return_value.exited = 0
        result = rs.exec("echo Hello")
        mock_conn.assert_called_once_with(host="localhost", user="user")
        mock_conn.return_value.run.assert_called_once()
        assert mock_conn.return_value.run.call_args[0][0] == "echo Hello"
        assert result == "Hello"


def test_RemoteShell_exec_fail():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell("localhost", "user")
        mock_conn.return_value.run.return_value.stdout = "Hello"
        mock_conn.return_value.run.return_value.stderr = "Error"
        mock_conn.return_value.run.return_value.failed = True
        mock_conn.return_value.run.return_value.exited = 1
        result = rs.exec("echo Hello")
        mock_conn.assert_called_once_with(host="localhost", user="user")
        mock_conn.return_value.run.assert_called_once()
        assert mock_conn.return_value.run.call_args[0][0] == "echo Hello"
        assert result == "Hello\nError: Error\nExit Code: 1"


def test_RemoteShell_get_host_info():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell("localhost", "user")
        mock_conn.return_value.run.side_effect = [
            MagicMock(stdout="Linux", stderr="", failed=False, exited=0),
            MagicMock(stdout="ID=ubuntu", stderr="", failed=False, exited=0),
            MagicMock(stdout="CPU", stderr="", failed=False, exited=0),
            MagicMock(stdout="groups", stderr="", failed=False, exited=0),
            MagicMock(
                stdout="User has sudo privileges", stderr="", failed=False, exited=0
            ),
        ]
        result = rs.get_host_info()
        mock_conn.assert_called_once_with(host="localhost", user="user")
        assert result == (
            '> uname -a\nLinux\n> cat /etc/os-release\nID=ubuntu\n> lscpu | grep -E \'Model name|CPU\(s\)\'\nCPU\n> groups\ngroups\n> sudo -n true 2>/dev/null && echo "User has sudo privileges" || echo "User lacks sudo privileges"\nUser has sudo privileges\n'
        )
