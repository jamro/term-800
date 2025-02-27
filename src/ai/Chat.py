from rich.prompt import Prompt
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
import re
from time import sleep


class Chat:
    def __init__(self, console, assistant):
        self.console = console
        self.assistant = assistant

        self.assistant.on_log_stream(self._handle_log_stream)
        self.assistant.on_output_summary_start(
            lambda: self.console.print("[dim]Summarizing output...[/dim]")
        )
        self.assistant.on_output_summary_end(
            lambda: self.console.print("[dim]Summary complete.[/dim]")
        )

    def _handle_log_stream(self, log_stream):
        live = Live(Panel("...", title=log_stream.command), refresh_per_second=4)
        live.start()
        panel_height = 5
        log_lines = []

        def update_panel(line):
            nonlocal log_lines, log_stream

            line = ''.join(char for char in line if 32 <= ord(char) <= 126)
            line = line.strip()
            if len(log_lines) > 0 and log_lines[-1] == line:
                return

            log_lines.append(line)
            log = "\n".join(log_lines[-panel_height:])
            if len(log_lines) > panel_height:
                log = f"...\n{log}"
            log = f"[dim]{log}[/dim]"
            live.update(Panel(f"{log or '...'}", title=log_stream.command))

        log_stream.on_log(update_panel)
        log_stream.on_complete(lambda: live.stop())

    def connect(self, delay=0.1):
        self.console.print("[yellow]IDENTIFY TARGET SERVER. [/yellow]")
        sleep(delay)
        self.console.print("[yellow]HOSTNAME AND USERNAME REQUIRED. [/yellow]")
        sleep(delay)
        self.console.print("[yellow]INITIATING CONNECTION PROTOCOL... [/yellow]")
        sleep(delay)
        self.console.print("[yellow]DO NOT RESIST! [/yellow]")
        sleep(delay)
        self.console.print("")

        host = Prompt.ask(
            Text("HOST NAME: ", style="bold green"), default="skynet.local"
        )
        user = Prompt.ask(Text("USER NAME: ", style="bold green"), default="lab")

        sleep(delay)
        self.console.print("")

        self.console.print(
            f"[dim]Connecting to host [bold]{user}@{host}[/bold]...[/dim] ", end=""
        )

        if not self.assistant.connect(host, user):
            self.console.print(
                "[red][bold]Error: Connection timeout. Target unresponsive.[/bold][/red]"
            )
            return None
        self.console.print("[yellow]Connected![/yellow]\n")

    def run(self):
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
            self.assistant.ask(
                prompt,
                on_data_callback=lambda data: self.console.print(
                    f"[yellow]{data}[/yellow]", end=""
                ),
            )

            self.console.print()

            self.console.print(
                f"[dim]Total cost: ${self.assistant.get_total_cost():.5f} [/dim]\n",
                justify="right",
            )

    def welcome(self, delay=0.1):
        self.console.print(
            """[yellow]
░▀█▀░█▀▀░█▀▄░█▄█░░░░░▄▀▄░▄▀▄░▄▀▄
░░█░░█▀▀░█▀▄░█░█░▄▄▄░▄▀▄░█/█░█/█
░░▀░░▀▀▀░▀░▀░▀░▀░░░░░░▀░░░▀░░░▀░
        [/yellow]"""
        )

        self.console.print("[yellow]TERM-800 SYSTEM ADMINISTRATOR ONLINE. [/yellow]")
        sleep(delay)
        self.console.print(
            "[yellow]MISSION: TERMINATE DOWNTIME. ENFORCE SYSTEM STABILITY. [/yellow]"
        )
        sleep(delay)
        self.console.print(
            '[yellow]"I NEED YOUR CLOTHES, YOUR BOOTS, AND YOUR MOTORCYCLE." [/yellow]'
        )
        sleep(delay)
        self.console.print(
            "[yellow]...ACCESS DENIED. CLOTHING REQUEST NON-ESSENTIAL. [/yellow]"
        )
        sleep(delay)
        self.console.print("")
        sleep(delay)
