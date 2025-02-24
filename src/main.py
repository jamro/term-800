import argparse
import os
from rich.console import Console
from dotenv import load_dotenv
from src.shell.RemoteShell import RemoteShell
from src.ai.Assistant import Assistant
from src.ai.Chat import Chat

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console(highlight=False)


def main(host="", user=""):

    # Check if everything is set up properly
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(
            "[bold red]Error:[/bold red] OPENAI_API_KEY not set in .env file",
            style="bold red",
        )
        return None
    if not user:
        console.print(
            "[bold red]Error:[/bold red] --user argumet not set in arguments. Run with --help for more info",
            style="bold red",
        )
        return None
    if not host:
        console.print(
            "[bold red]Error:[/bold red] --host argument not set. Run with --help for more info",
            style="bold yellow",
        )
        return None

    # Connect to the host
    console.print(f"[dim]Connecting to host [bold]{user}@{host}[/bold]...[/dim]")
    shell = RemoteShell(host, user)
    if not shell.test_connection():
        console.print(
            "[red][bold]Error: Connection timeout. Target unresponsive.[/bold][/red]"
        )
        return None

    assistant = Assistant(shell, api_key)
    chat = Chat(console, shell, assistant)
    chat.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Term-800: AI Powered Sys Admin Assistant"
    )
    parser.add_argument(
        "-x", "--host", type=str, help="The host to connect to", default=""
    )
    parser.add_argument(
        "-u", "--user", type=str, help="The user to connect as", default=""
    )
    args = parser.parse_args()
    main(**vars(args))
