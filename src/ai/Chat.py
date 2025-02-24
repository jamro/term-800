from rich.prompt import Prompt
from rich.text import Text


class Chat:
    def __init__(self, console, shell, assistant):
        self.console = console
        self.shell = shell
        self.assistant = assistant

        def print_output(output):
            nonlocal self
            lines = output.split("\n")
            if len(lines) > 3:
                output = "\n".join(lines[:3]) + "\n..."
            else:
                output = "\n".join(lines)
            output = output[:100] + "..." if len(output) > 100 else output

            self.console.print(f"[dim]{output}[/dim]")

        self.assistant.on_exec_prompt = lambda input: self.console.print(
            f"> [dim bold]{input}[/dim bold]"
        )
        self.assistant.on_exec_response = print_output

    def run(self):

        self.console.print("[bold yellow]Term-800 Online.[/bold yellow]")
        self.console.print("[yellow]AI-driven system administrator activated.[/yellow]")

        self.console.print(
            """[yellow]
░▀█▀░█▀▀░█▀▄░█▄█░░░░░▄▀▄░▄▀▄░▄▀▄
░░█░░█▀▀░█▀▄░█░█░▄▄▄░▄▀▄░█/█░█/█
░░▀░░▀▀▀░▀░▀░▀░▀░░░░░░▀░░░▀░░░▀░
        [/yellow]"""
        )

        self.console.print(
            "[yellow]T-800: “[bold]I need your clothes, your boots, and your motorcycle.[/bold]”[/yellow]"
        )
        self.console.print("")
        self.console.print("[dim]Type /help to see available system functions.[/dim]")
        self.console.print("[dim]Type /bye to terminate my session.[/dim]")
        self.console.print("")
        self.console.print(
            "[bold yellow][ Standing by for instructions. ][/bold yellow]"
        )
        self.console.print("\n")

        while True:
            prompt = Prompt.ask(Text("$>", style="bold green"))

            if prompt == "/bye":
                self.console.print("[yellow]Hasta la vista![/yellow]")
                return

            self.console.print(f"[bold yellow]{prompt}[/bold yellow]")
            reply = self.assistant.ask(prompt)
            self.console.print(f"[yellow]{reply}[/yellow]")

            self.console.print(
                f"[dim]Total cost: ${self.assistant.get_total_cost():.5f} [/dim]\n",
                justify="right",
            )
