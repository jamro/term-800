from fabric import Connection
from src.shell.LogStream import LogStream
from paramiko.ssh_exception import AuthenticationException
import re


class RemoteShell:

    def __init__(self):
        self.host = None
        self.user = None
        self.conn = None

    def connect(self, host, user, passwd=None):
        self.host = host
        self.user = user
        connect_kwargs = {}
        if passwd:
            connect_kwargs["password"] = passwd

        self.conn = Connection(host=host, user=user, connect_kwargs=connect_kwargs)

        try:
            self.conn.open()
        except AuthenticationException:
            return "AUTH_ERROR"
        except Exception as e:
            return "Error: " + str(e)
        return "OK"

    def _apply_r(self, text):
        lines = text.split("\n")
        processed_lines = []

        for line in lines:
            final_line = []
            index = 0  # Tracks position for overwriting

            for char in line:
                if char == "\r":
                    index = 0  # Move cursor to the beginning
                else:
                    if index < len(final_line):
                        final_line[index] = char  # Overwrite character
                    else:
                        final_line.append(char)  # Append new character
                    index += 1

            processed_lines.append("".join(final_line))

        return "\n".join(processed_lines)

    def exec(self, command, log_stream=None):
        if not self.conn:
            raise Exception("Not connected to a host")
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

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        full_output = ansi_escape.sub("", full_output)
        full_output = self._apply_r(full_output)
        full_output = re.sub(r"\n\n+", "\n", full_output)

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

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        self.host = None
        self.user = None
