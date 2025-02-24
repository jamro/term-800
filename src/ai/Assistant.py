from .Conversation import Conversation
from .TokenPricing import TokenPricing


class Assistant(Conversation):

    def __init__(self, shell, api_key):
        system_message = """
            You are system admin connected to a remote linux host ({shell.host}) over SSH. Your login is {shell.user}. 
            You answer question and perform tasks on the remote host via SSH.
            Communication style: style is concise, robotic, and emotionless, delivering information in a direct, tactical manner with a focus on task objectives and status updates.
        """

        super().__init__(api_key, system_message=system_message)
        self.on_exec_prompt = lambda input: None
        self.on_exec_response = lambda output: None
        self.tokenPricing = TokenPricing()

        def run_shell_command(command):
            nonlocal self
            self.on_exec_prompt(command)
            output = shell.exec(command)
            self.on_exec_response(output)
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

    def get_total_cost(self):
        return self.tokenPricing.get_total_cost(self.token_stats)
