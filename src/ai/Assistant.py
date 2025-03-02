from src.ai.Conversation import Conversation
from src.ai.TokenPricing import TokenPricing
from src.shell.LogStream import LogStream
from src.ai.ExecGuardian import ExecGuardian
from src.ai.thoughts import (
    EntryThought,
    QueryThought,
    AnswerValidateThought,
    ComplexityThought,
    PlanThought,
)
from pyee import EventEmitter

EXEC_GUIDELINES_PROMPT = """
# Task Execution Guidelines:
  - You execute all necessary shell commands yourself. Never ask the user to execute commands. Never include commands in the response.
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

    def __init__(self, shell, settings, api_key):
        self.shell = shell
        self.settings = settings
        super().__init__(api_key, model_name=settings.get("llm_model"))
        self.tokenPricing = TokenPricing()
        self.emitter = EventEmitter()
        self._chain_of_thoughts_log = []
        self.abort_mode = False
        self.guardian = ExecGuardian(
            api_key=api_key,
            settings=settings,
            model_name=settings.get("llm_model"),
            token_stats=self.token_stats,
        )

        def run_shell_command(command):
            nonlocal self
            log_stream = LogStream(command)
            log_stream.command = command
            command_allowed = self.guardian.is_allowed(command)
            self.emitter.emit("log_stream", log_stream)
            if command_allowed:
                try:
                    output = shell.exec(command, log_stream=log_stream)
                except Exception as e:
                    output = f"Error: {str(e)}"
                    self.abort_mode = True
                    log_stream.write(output)
                    log_stream.done()
            else:
                self.abort_mode = True
                output = "Command execution was aborted by the user. Next action: Abort execution of the current operation. Do not execute further commands."
                log_stream.write("Command execution was aborted by the user")
                log_stream.done()

            if len(output) > 5000:
                summary_convo = Conversation(
                    self.api_key,
                    model_name=self.model_name,
                    token_stats=self.token_stats,
                )
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
              {POST_EXEC_PROMPT if not self.abort_mode else "Do not execute further commands. Command execution was aborted by the user."}
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

    def think(
        self,
        query,
        model_name=None,
        on_data_callback=None,
        on_plan_callback=None,
        prepare_plan=True,
    ):
        self.abort_mode = False
        entry_node = EntryThought()
        main_query_node = QueryThought(
            assistant=self,
            post_exec_prompt=POST_EXEC_PROMPT,
            model_name=model_name,
            on_data_callback=on_data_callback,
        )
        validate_node = AnswerValidateThought(
            assistant=self,
            model_name=model_name,
        )
        complexity_node = ComplexityThought(
            assistant=self,
            model_name=model_name,
        )
        plan_node = PlanThought(
            assistant=self,
            model_name=model_name,
            on_data_callback=on_plan_callback,
        )

        entry_node.connect(main_query_node, lambda x: not x["prepare_plan"])
        entry_node.connect(complexity_node, lambda x: x["prepare_plan"])
        complexity_node.connect(plan_node, lambda x: x["complexity"] == "COMPLEX")
        complexity_node.connect(main_query_node, lambda x: x["complexity"] != "COMPLEX")
        plan_node.connect(main_query_node)
        main_query_node.connect(validate_node, lambda x: not self.abort_mode)
        validate_node.connect(
            main_query_node, lambda x: x["next_node"] == "NEXT" and not self.abort_mode
        )

        output = entry_node.execute(
            {
                "query": query,
                "prepare_plan": prepare_plan,
            }
        )

        self._chain_of_thoughts_log = entry_node.log
        self.abort_mode = False

        return output["response"]

    def on_log_stream(self, handler):
        self.emitter.on("log_stream", handler)

    def on_output_summary_start(self, handler):
        self.emitter.on("output_summary_start", handler)

    def on_output_summary_end(self, handler):
        self.emitter.on("output_summary_end", handler)

    def get_total_cost(self):
        return self.tokenPricing.get_total_cost(self.token_stats)

    def connect(self, host, user, passwd=None):
        result = self.shell.connect(host, user, passwd)
        if result != "OK":
            return result

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

        return "OK"

    def close(self):
        self.shell.close()

    def get_chain_of_thoughts_log(self):
        return self._chain_of_thoughts_log
