from fabric import Connection
from src.shell.LogStream import LogStream


class RemoteShell:

    def __init__(self, host, user):
        self.host = host
        self.user = user
        self.conn = Connection(host=host, user=user)

    def test_connection(self):
        try:
            self.conn.open()
        except Exception:
            return False
        return True

    def exec(self, command, log_stream=None):
        log_stream = log_stream or LogStream(command)
        log_stream.command = command

        result = self.conn.run(
            command,
            hide=True,
            warn=True,
            pty=True,
            out_stream=log_stream,
            err_stream=log_stream,
        )
        log_stream.done()
        full_output = ""
        if result.stdout:
            full_output += result.stdout
        if result.stderr:
            full_output += f"\nError: {result.stderr}"
        if result.failed:
            full_output += f"\nExit Code: {result.exited}"
        return full_output

    def get_host_info(self):
        info_cmds = [
            "uname -a",
            "cat /etc/os-release",
            "lscpu | grep -E 'Model name|CPU\(s\)'",
            "groups",
            'sudo -n true 2>/dev/null && echo "User has sudo privileges" || echo "User lacks sudo privileges"',
        ]
        basic_info = ""
        for cmd in info_cmds:
            basic_info += f"> {cmd}\n{self.exec(cmd)}\n"

        return basic_info
