from src.chat.Chat import Chat


class CmdChat(Chat):
    def __init__(self, console, assistant):
        super().__init__(console, assistant)

    def _handle_prompt(self, prompt):
        if not prompt.startswith("/"):
            super()._handle_prompt(prompt)
            return
        
        command = prompt[1:]

        if command == "bye":
            self._handle_bye_command()
        elif command == "help":
            self._handle_help_command()
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
        self.console.print("")
        self.console.print('[dim]"Come with me if you want to execute commands."[/dim]')
        self.console.print("")
