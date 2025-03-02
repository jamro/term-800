from rich.prompt import Prompt
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from time import sleep
import re


class Chat:
    def __init__(self, console, settings, assistant):
        self.console = console
        self.assistant = assistant
        self._is_running = False
        self.settings = settings

        self.assistant.on_log_stream(self._handle_log_stream)
        self.assistant.on_output_summary_start(
            lambda: self.console.print("[dim]Summarizing output...[/dim]")
        )
        self.assistant.on_output_summary_end(
            lambda: self.console.print("[dim]Summary complete.[/dim]")
        )

        self.assistant.guardian.confirm_execution = self._confirm_execution

    def _confirm_execution(self, command, details):
        # are you sure? yes no  question. by default, yes is selected
        self.console.print("")
        answer = Prompt.ask(
            f"[green]Are you sure you want to execute command [bold red]{command}[/bold red]? {details}[/green]",
            choices=["y", "n"],
            default="y",
        )
        return answer == "y"

    def _handle_log_stream(self, log_stream):
        self.console.print()
        live = Live(Panel("...", title=log_stream.command), refresh_per_second=4)
        live.start()
        panel_height = 5
        log_lines = [""]

        def update_panel(line):
            nonlocal log_lines, log_stream

            add_newline = line.endswith(
                "\n"
            )  # if the line ends with a newline, we want to add a new line to the log

            # remove ansi escape codes (e.g. color codes) from the line
            ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
            line = ansi_escape.sub("", line)

            # remove non-printable characters from the line
            line = "".join(char for char in line if 32 <= ord(char) <= 126)
            line = line.strip()

            # if the line is the same as the last line, we don't need to update the log
            if len(log_lines) > 1 and log_lines[-2].strip() == line.strip():
                return

            # if the line is not the same as the last line, we update the log
            # we overwrite the last line in the log with the new text to simulate \r behavior
            log_lines[-1] = line

            # if the line ends with a newline, we add a new line to the log
            if add_newline and log_lines[-1] != "":
                log_lines.append("")

            log = "\n".join(log_lines[-panel_height:])
            if log.endswith(
                "\n"
            ):  # remove trailing newline before printing in the panel
                log = log[:-1]

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

        default_host = self.settings.get("host") or "skynet.local"
        default_user = self.settings.get("user") or "lab"

        host = Prompt.ask(Text("HOST NAME: ", style="bold green"), default=default_host)
        user = Prompt.ask(Text("USER NAME: ", style="bold green"), default=default_user)

        self.settings.set("host", host)
        self.settings.set("user", user)

        sleep(delay)
        self.console.print("")

        self.console.print(
            f"[dim]Connecting to host [bold]{user}@{host}[/bold]...[/dim] ", end=""
        )

        connect_result = self.assistant.connect(host, user)
        if connect_result == "OK":
            pass
        elif connect_result == "AUTH_ERROR":
            # ask for password
            self.console.print("[dim]Authentication required.[/dim]")
            while connect_result == "AUTH_ERROR":
                passwd = Prompt.ask(Text("PASSWORD", style="bold green"), password=True)
                connect_result = self.assistant.connect(host, user, passwd)
            self.console.print("[dim]Authorizing... [/dim] ", end="")

        else:
            self.console.print(f"[red][bold]{connect_result}[/bold][/red]")
            return False
        self.console.print("[yellow]Connected![/yellow]\n")
        return True

    def run(self):
        self._is_running = True
        self.console.print("[dim]Type /help to see available system functions.[/dim]")
        self.console.print("[dim]Type /bye to terminate my session.[/dim]")
        self.console.print("")
        self.console.print(f"[dim]Model: {self.settings.get('llm_model')}[/dim]")
        self.console.print("")
        self.console.print(
            "[bold yellow][ Standing by for instructions. ][/bold yellow]"
        )
        self.console.print("\n")

        while self._is_running:
            prompt = Prompt.ask(
                Text(
                    f"{self.assistant.shell.user}@{self.assistant.shell.host} $>",
                    style="bold green",
                )
            )
            self._handle_prompt(prompt)

    def _handle_prompt(self, prompt):
        if prompt == "/bye":
            self._is_running = False
            return
        try:
            self.assistant.think(
                prompt,
                on_data_callback=lambda data: self.console.print(
                    f"[yellow]{data}[/yellow]", end=""
                ),
                on_plan_callback=lambda data: self.console.print(
                    f"[green]{data}[/green]", end=""
                ),
            )
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.print()

        self.console.print(
            f"[dim]Total cost: ${self.assistant.get_total_cost():.5f} [/dim]\n",
            justify="right",
        )

    def welcome(self, delay=0.1):
        self.console.print(
            """[red]
                       ▄▄
                     ▄▄▄▄▄▄▄
                   ▄▄▄▄▄▄▄▄▄▄▄
                  ▄▄▄▄▄▄▄▄▄▄▄▄▄
               ▄   ▄▄▄▄▄▄▄▄▄▄▄   ▄
             ▄▄▄▄▄   ▄▄▄▄▄▄▄   ▄▄▄▄▄
           ▄▄▄▄▄▄▄▄▄   ▄▄▄   ▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
       ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
     ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
[/red]
[white]                 Powered by [bold]SKYNET[/bold][/white]"""
        )
        self.console.print(
            """[red]
░░░░░░░░░▀█▀░█▀▀░█▀▄░█▄█░░░░░▄▀▄░▄▀▄░▄▀▄░░░░░░░░░
░░░░░░░░░░█░░█▀▀░█▀▄░█░█░▄▄▄░▄▀▄░█/█░█/█░░░░░░░░░
░░░░░░░░░░▀░░▀▀▀░▀░▀░▀░▀░░░░░░▀░░░▀░░░▀░░░░░░░░░░
        [/red]"""
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
