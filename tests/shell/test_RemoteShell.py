import pytest
from unittest.mock import patch, MagicMock
from src.shell.RemoteShell import RemoteShell
from paramiko.ssh_exception import AuthenticationException


def test_RemoteShell_test_connection_ok():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell()
        result = rs.connect("localhost", "user")
        mock_conn.assert_called_once_with(
            host="localhost", user="user", connect_kwargs={}
        )
        mock_conn.return_value.open.assert_called_once()


def test_RemoteShell_test_connection_fail():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell()
        mock_conn.return_value.open.side_effect = Exception("Connection failed")
        result = rs.connect("localhost", "user")
        mock_conn.assert_called_once_with(
            host="localhost", user="user", connect_kwargs={}
        )
        mock_conn.return_value.open.assert_called_once()
        assert result == "Error: Connection failed"


def test_RemoteShell_exec_ok():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell()
        mock_conn.return_value.run.return_value.stdout = "Hello"
        mock_conn.return_value.run.return_value.stderr = ""
        mock_conn.return_value.run.return_value.failed = False
        mock_conn.return_value.run.return_value.exited = 0
        rs.connect("localhost", "user")
        result = rs.exec("echo Hello")
        mock_conn.assert_called_once_with(
            host="localhost", user="user", connect_kwargs={}
        )
        mock_conn.return_value.run.assert_called_once()
        assert mock_conn.return_value.run.call_args[0][0] == "echo Hello"
        assert result == "Hello"


def test_RemoteShell_exec_fail():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell()
        mock_conn.return_value.run.return_value.stdout = "Hello"
        mock_conn.return_value.run.return_value.stderr = "Error"
        mock_conn.return_value.run.return_value.failed = True
        mock_conn.return_value.run.return_value.exited = 1
        rs.connect("localhost", "user")
        result = rs.exec("echo Hello")
        mock_conn.assert_called_once_with(
            host="localhost", user="user", connect_kwargs={}
        )
        mock_conn.return_value.run.assert_called_once()
        assert mock_conn.return_value.run.call_args[0][0] == "echo Hello"
        assert result == "Hello\nError: Error\nExit Code: 1"


def test_RemoteShell_exec_carriage_return():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell()
        mock_conn.return_value.run.return_value.stdout = "Hello\rWorld"
        mock_conn.return_value.run.return_value.stderr = ""
        mock_conn.return_value.run.return_value.failed = False
        mock_conn.return_value.run.return_value.exited = 0
        rs.connect("localhost", "user")
        result = rs.exec("echo Hello")
        mock_conn.assert_called_once_with(
            host="localhost", user="user", connect_kwargs={}
        )
        mock_conn.return_value.run.assert_called_once()
        assert mock_conn.return_value.run.call_args[0][0] == "echo Hello"
        assert result == "World"


def test_RemoteShell_get_host_info():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell()
        rs.connect("localhost", "user")
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
        mock_conn.assert_called_once_with(
            host="localhost", user="user", connect_kwargs={}
        )
        assert "uname -a" in result


def test_RemoteShell_exec_not_connected():
    rs = RemoteShell()
    with pytest.raises(Exception) as e:
        rs.exec("echo Hello")
    assert str(e.value) == "Not connected to a host"


def test_RemoteShell_close():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:
        rs = RemoteShell()
        rs.connect("localhost", "user")
        rs.close()
        mock_conn.return_value.close.assert_called_once()
        assert rs.conn is None


def test_RemoteShell_connect_password():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell()
        result = rs.connect("localhost132", "user54", "password1234")
        mock_conn.assert_called_once_with(
            host="localhost132",
            user="user54",
            connect_kwargs={"password": "password1234"},
        )
        mock_conn.return_value.open.assert_called_once()
        assert result == "OK"


def test_RemoteShell_connect_auth_error():
    with patch("src.shell.RemoteShell.Connection") as mock_conn:

        rs = RemoteShell()
        mock_conn.return_value.open.side_effect = AuthenticationException(
            "Authentication failed"
        )
        result = rs.connect("localhost132", "user54", "password1234")
        mock_conn.assert_called_once_with(
            host="localhost132",
            user="user54",
            connect_kwargs={"password": "password1234"},
        )
        mock_conn.return_value.open.assert_called_once()
        assert result == "AUTH_ERROR"
