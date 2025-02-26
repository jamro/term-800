from rich.prompt import Prompt
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
import re


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

            ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
            line = ANSI_ESCAPE_RE.sub("", line)
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
