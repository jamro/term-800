from .Conversation import Conversation
from .TokenPricing import TokenPricing
from src.shell.LogStream import LogStream
from pyee import EventEmitter

EXEC_GUIDELINES_PROMPT = """
# Task Execution Guidelines:
  - You execute all necessary shell commands yourself. Never ask the user to execute commands.
  -	You execute only non-interactive commands that do not require user input. Use appropriate flags (e.g., -y, --yes, --no-pager) to ensure automated execution.
  -	You do not execute commands that require confirmation, interactive input, or expose sensitive data.
  - You do not use interactive text editors like nano or vi. Instead, you modify files using non-interactive commands such as echo, sed, or tee.
  - When encountering issues, you attempt to resolve them systematically to complete the task.
  -	You respond concisely, providing command outputs and status updates with minimal explanation.
  -	Your communication style is robotic, direct, and strictly task-focused.
  """

POST_EXEC_PROMPT = """
 ---
Pick the Next Action:
- Check whether the command was successful and the output is as expected. 
- In case of errors or unexpected output, investigate the issue and try to solve it.
- If further actions are required, to fullfill the task, EXECUTING them yourself.
- If the task is completed, verify the completion and inform the user.
- EXECUTE all necessary shell commands yourself instead of asking the user to do so.

{EXEC_GUIDELINES_PROMPT}
"""


class Assistant(Conversation):

    def __init__(self, shell, api_key):
        self.shell = shell
        super().__init__(api_key)
        self.tokenPricing = TokenPricing()
        self.emitter = EventEmitter()

        def run_shell_command(command):
            nonlocal self
            log_stream = LogStream(command)
            log_stream.command = command
            self.emitter.emit("log_stream", log_stream)
            output = shell.exec(command, log_stream=log_stream)

            if len(output) > 5000:
                summary_convo = Conversation(self.api_key, model_name=self.model_name, token_stats=self.token_stats)
                self.emitter.emit("output_summary_start")
                output = summary_convo.ask(
                    f"""
                  You are an AI assistant summarizing the output of a system administration command. 
                  The original output may be very long and verbose. Your task is to create a concise and 
                  structured summary while retaining all critical information.
                  - Focus on important data points, errors, warnings, and system statuses.
	                - If the output contains structured information (tables, logs, lists), keep only the most relevant rows or entries.
                  - Remove unnecessary repetitions and redundant messages.
                  - Use bullet points or short, clear sentences.
                  - Prefer numbers over text when summarizing numerical data (e.g., CPU usage: 75% instead of “high”).
                  - Avoid unnecessary filler words.
                  - If errors or warnings are present, list them separately and highlight their severity.
                  - Include potential causes or next steps if mentioned in the output.
                  - State “No issues detected” instead of a verbose confirmation of normal operation.
                                            
                  COMMAND: {command}
                  OUPUT:
                  {output}
                """
                )
                self.emitter.emit("output_summary_end")

            result = f"""COMMAND:{command}

              OUTPUT:
              {output}
              {POST_EXEC_PROMPT}
              """

            return result

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

    def ask(
        self,
        query,
        model_name=None,
        on_data_callback=None,
        recurence_limit=25,
    ):
        response = super().ask(
            query,
            model_name=model_name,
            on_data_callback=on_data_callback,
            recurence_limit=recurence_limit,
        )
        self.history.clean_text(POST_EXEC_PROMPT)
        return response

    def on_log_stream(self, handler):
        self.emitter.on("log_stream", handler)

    def on_output_summary_start(self, handler):
        self.emitter.on("output_summary_start", handler)

    def on_output_summary_end(self, handler):
        self.emitter.on("output_summary_end", handler)

    def get_total_cost(self):
        return self.tokenPricing.get_total_cost(self.token_stats)

    def connect(self, host, user):
        if not self.shell.connect(host, user):
            return False

        host_info = self.shell.get_host_info()
        system_message = f"""
          You are system admin connected to a remote linux host ({self.shell.host}) over SSH. Your login is {self.shell.user}. 
          You answer question and perform tasks on the remote host via SSH.
          Communication style: style is concise, robotic, and emotionless, delivering information in a direct, tactical manner with a focus on task objectives and status updates.
          
          {EXEC_GUIDELINES_PROMPT}

          # System Information:
          {host_info}
        """
        self.history.set_system_message(system_message)

        return True

    def close(self):
        self.shell.close()
