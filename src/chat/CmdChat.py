from src.chat.Chat import Chat
import json
from src.ai.Conversation import Conversation


class CmdChat(Chat):
    def __init__(self, console, settings, assistant):
        self.settings = settings
        self.assistant = assistant
        super().__init__(console, settings, assistant)

    def _handle_prompt(self, prompt):
        if not prompt.startswith("/"):
            super()._handle_prompt(prompt)
            return

        command = prompt[1:].split(" ")

        if command[0] == "bye":
            self._handle_bye_command()
        elif command[0] == "help":
            self._handle_help_command()
        elif command[0] == "model":
            self._handle_llm_model(command)
        elif command[0] == "clear":
            self._handle_clear()
        elif command[0] == "debug":
            self._handle_debug()
        elif command[0] == "guard":
            self._handle_guard(command)
        else:
            self.console.print(
                f"[bold red]Command not found: '{command}'. Type /help for available commands.[/bold red]"
            )

    def _handle_bye_command(self):
        self.console.print("[dim]Terminating session...[/dim]")
        self.assistant.close()
        self.console.print("[dim]Session terminated.[/dim]")
        self.console.print("[yellow]Hasta la vista![/yellow]")
        self._is_running = False

    def _handle_help_command(self):
        self.console.print("[yellow]Available commands - choose wisely:[/yellow]")
        self.console.print()
        self.console.print("[yellow][bold]/bye[/bold]: Terminate the session[/yellow]")
        self.console.print(
            "[yellow][bold]/help[/bold]: Display this help message[/yellow]"
        )
        self.console.print(
            "[yellow][bold]/model <llm_model>[/bold]: Change the language model[/yellow]"
        )
        self.console.print(
            "[yellow][bold]/clear[/bold]: clear the conversation history starting chat[/yellow]"
        )
        self.console.print(
            "[yellow][bold]/guard <on|auto|off>[/bold]: ask user to confirm commands execution[/yellow]"
        )
        self.console.print(
            "[yellow][bold]/debug[/bold]: print raw LLM conversation history[/yellow]"
        )
        self.console.print("")
        self.console.print('[dim]"Come with me if you want to execute commands."[/dim]')
        self.console.print("")

    def _handle_llm_model(self, command):
        supported_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        if len(command) < 2:
            self.console.print(
                f"[yellow]Current LLM model: [bold]{self.assistant.model_name}[/bold][/yellow]"
            )
            self.console.print("")
            self.console.print(
                "[yellow]To change the language model, type: [bold]/model <llm_model>[/bold][/yellow]"
            )
            self.console.print(
                f"[dim]Suggested models: [bold]{', '.join(supported_models)}[/bold][/dim]"
            )
            self.console.print("")
            return

        try:
            self.console.print(f"[dim]Verifying language model '{command[1]}'...[/dim]")
            test_convo = Conversation(
                api_key=self.assistant.api_key, model_name=command[1]
            )
            test_convo.add_function(
                name="verify_model",
                description="Verify whether the model is supported",
                logic=lambda: "Model is supported",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            )
            test_convo.ask("verify_model")
        except Exception as e:
            self.console.print(
                f"[bold red]Unsupported language model: '{command[1]}'. Suggested models: {supported_models}[/bold red]"
            )
            self.console.print(f"[red]{str(e)}[/red]")
            return

        self.settings.set("llm_model", command[1])
        self.assistant.model_name = command[1]
        self.console.print(f"[dim]Language model changed to '{command[1]}'.[/dim]")

    def _handle_debug(self):
        items = self.assistant.history.get_items()
        self.console.print("----- CONVERSATION HISTORY -----")
        self.console.print(json.dumps(items, indent=4), highlight=True)
        self.console.print("----- CHAIN OF THOUGHTS LOG -----")
        get_chain_of_thoughts_log = self.assistant.get_chain_of_thoughts_log()
        for log in get_chain_of_thoughts_log:
            self.console.print(
                f"----- [bold]{log['step']}[/bold] ------------------------------------"
            )
            self.console.print(
                "[bold]>>> INPUT:  [/bold]" + json.dumps(log["input"], indent=4),
                highlight=True,
            )
            self.console.print(
                "[bold]>>> OUTPUT: [/bold]" + json.dumps(log["output"], indent=4),
                highlight=True,
            )

    def _handle_clear(self):
        self.assistant.history.clear()
        self.console.print("[dim]Conversation history cleared.[/dim]")

    def _handle_guard(self, command):
        if len(command) < 2:
            self.console.print(
                f"[yellow]Execution guardian is [bold]{self.settings.get('guard')}[/bold][/yellow]"
            )
            self.console.print("")
            self.console.print(
                "[yellow]To change the execution guardian, type: [bold]/guard <on|auto|off>[/bold][/yellow]"
            )
            self.console.print("")
            return

        if command[1] not in ["on", "auto", "off"]:
            self.console.print(
                f"[bold red]Invalid guardian mode: '{command[1]}'. Choose from: on, auto, off[/bold red]"
            )
            return

        self.settings.set("guard", command[1])
        self.console.print(f"[dim]Execution guardian set to '{command[1]}'.[/dim]")
