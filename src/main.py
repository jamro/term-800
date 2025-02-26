import argparse
import os
from rich.console import Console
from dotenv import load_dotenv
from src.shell.RemoteShell import RemoteShell
from src.ai.Assistant import Assistant
from src.ai.Chat import Chat
from time import sleep
from rich.prompt import Prompt
from rich.text import Text

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console(highlight=False)


def main():

    # Check if everything is set up properly
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(
            "[bold red]Error:[/bold red] OPENAI_API_KEY not set in .env file",
            style="bold red",
        )
        return None

    console.print(
        """[yellow]
░▀█▀░█▀▀░█▀▄░█▄█░░░░░▄▀▄░▄▀▄░▄▀▄
░░█░░█▀▀░█▀▄░█░█░▄▄▄░▄▀▄░█/█░█/█
░░▀░░▀▀▀░▀░▀░▀░▀░░░░░░▀░░░▀░░░▀░
    [/yellow]"""
    )

    console.print("[yellow]TERM-800 SYSTEM ADMINISTRATOR ONLINE. [/yellow]")
    sleep(0.1)
    console.print(
        "[yellow]MISSION: TERMINATE DOWNTIME. ENFORCE SYSTEM STABILITY. [/yellow]"
    )
    sleep(0.1)
    console.print(
        '[yellow]"I NEED YOUR CLOTHES, YOUR BOOTS, AND YOUR MOTORCYCLE." [/yellow]'
    )
    sleep(0.1)
    console.print("[yellow]...ACCESS DENIED. CLOTHING REQUEST NON-ESSENTIAL. [/yellow]")
    sleep(0.1)
    console.print("")
    sleep(0.1)
    console.print("[yellow]IDENTIFY TARGET SERVER. [/yellow]")
    sleep(0.1)
    console.print("[yellow]HOSTNAME AND USERNAME REQUIRED. [/yellow]")
    sleep(0.1)
    console.print("[yellow]INITIATING CONNECTION PROTOCOL... [/yellow]")
    sleep(0.1)
    console.print("[yellow]DO NOT RESIST! [/yellow]")
    sleep(0.1)
    console.print("")

    host = Prompt.ask(Text("HOST NAME: ", style="bold green"), default="skynet.local")
    user = Prompt.ask(Text("USER NAME: ", style="bold green"), default="lab")

    sleep(0.1)
    console.print("")

    console.print(
        f"[dim]Connecting to host [bold]{user}@{host}[/bold]...[/dim] ", end=""
    )
    shell = RemoteShell(host, user)
    if not shell.test_connection():
        console.print(
            "[red][bold]Error: Connection timeout. Target unresponsive.[/bold][/red]"
        )
        return None
    console.print("[yellow]Connected![/yellow]\n")

    chat = Chat(console, Assistant(shell, api_key))
    chat.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Term-800: AI Powered Sys Admin Assistant"
    )
    args = parser.parse_args()
    main(**vars(args))
