from src.chat.Chat import Chat
import json


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
            "[yellow][bold]/debug[/bold]: print raw LLM conversation history[/yellow]"
        )
        self.console.print("")
        self.console.print('[dim]"Come with me if you want to execute commands."[/dim]')
        self.console.print("")

    def _handle_llm_model(self, command):
        if len(command) < 2:
            self.console.print(
                f"[bold red]Missing argument: Please provide a language model name. Current model: '{self.assistant.model_name}'[/bold red]"
            )
            return

        supported_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

        if command[1] not in supported_models:
            self.console.print(
                f"[bold red]Unsupported language model: '{command[1]}'. Supported models: {supported_models}[/bold red]"
            )
            return

        self.settings.set("llm_model", command[1])
        self.assistant.model_name = command[1]
        self.console.print(f"[dim]Language model changed to '{command[1]}'.[/dim]")

    def _handle_debug(self):
        items = self.assistant.history.get_items()
        self.console.print("----- CONVERSATION HISTORY -----")
        self.console.print(json.dumps(items, indent=4), highlight=True)

    def _handle_clear(self):
        self.assistant.history.clear()
        self.console.print("[dim]Conversation history cleared.[/dim]")
