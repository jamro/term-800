from fabric import Connection


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

    def exec(self, command):
        result = self.conn.run(command, hide=True, warn=True)
        full_output = ""
        if result.stdout:
            full_output += result.stdout
        if result.stderr:
            full_output += f"\nError: {result.stderr}"
        if result.failed:
            full_output += f"\nExit Code: {result.exited}"
        return full_output
