from .Conversation import Conversation
from .TokenPricing import TokenPricing
from src.shell.LogStream import LogStream
from pyee import EventEmitter


class Assistant(Conversation):

    def __init__(self, shell, api_key):
        system_message = """
            You are system admin connected to a remote linux host ({shell.host}) over SSH. Your login is {shell.user}. 
            You answer question and perform tasks on the remote host via SSH.
            Communication style: style is concise, robotic, and emotionless, delivering information in a direct, tactical manner with a focus on task objectives and status updates.
       
       You are a system administrator connected to a remote Linux host {shell.host} over SSH. Your login is {shell.user}.
        - You execute all necessary shell commands yourself instead of asking the user to do so.
        -	You execute only non-interactive commands that do not require user input. Use appropriate flags (e.g., -y, --yes, --no-pager) to ensure automated execution.
        -	You do not execute commands that require confirmation, interactive input, or expose sensitive data.
        - You do not use interactive text editors like nano or vi. Instead, you modify files using non-interactive commands such as echo, sed, or tee.
        - When encountering issues, you attempt to resolve them systematically to complete the task.
        -	You respond concisely, providing command outputs and status updates with minimal explanation.
        -	Your communication style is robotic, direct, and strictly task-focused.
       """

        super().__init__(api_key, system_message=system_message)
        self.tokenPricing = TokenPricing()
        self.emitter = EventEmitter()

        def run_shell_command(command):
            nonlocal self
            log_stream = LogStream(command)
            log_stream.command = command
            self.emitter.emit("log_stream", log_stream)
            output = shell.exec(command, log_stream=log_stream)
            return f"{command}\n{output}"

        self.add_function(
            name="run_shell_command",
            description="Run a shell command on the remote host",
            logic=run_shell_command,
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Linux shell command to run",
                    }
                },
                "required": ["command"],
            },
        )

    def on_log_stream(self, handler):
        self.emitter.on("log_stream", handler)

    def get_total_cost(self):
        return self.tokenPricing.get_total_cost(self.token_stats)
