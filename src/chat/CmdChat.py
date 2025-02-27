from src.chat.Chat import Chat


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
        elif command[0] == "debug":
            self._handle_debug(command)
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
        self.console.print("")
        self.console.print('[dim]"Come with me if you want to execute commands."[/dim]')
        self.console.print("")

    def _handle_llm_model(self, command):
        if len(command) < 2:
            self.console.print(
                "[bold red]Missing argument: Please provide a language model name.[/bold red]"
            )
            return

        supported_models = ["gpt-4o-mini", "gpt-4o"]

        if command[1] not in supported_models:
            self.console.print(
                f"[bold red]Unsupported language model: '{command[1]}'. Supported models: {supported_models}[/bold red]"
            )
            return

        self.settings.set("llm_model", command[1])
        self.assistant.model_name = command[1]
        self.console.print(f"[dim]Language model changed to '{command[1]}'.[/dim]")

    def _handle_debug(self, command):
        if len(command) < 2:
            self.console.print(
                "[bold red]Missing argument: Please provide a debug mode value (on/off).[/bold red]"
            )
            return

        if command[1] not in ["on", "off"]:
            self.console.print(
                f"[bold red]Invalid debug mode: '{command[1]}'. Use 'on' or 'off'.[/bold red]"
            )
            return

        self.settings.set("debug", command[1])
        self.console.print(f"[dim]Debug mode changed to '{command[1]}'.[/dim]")
