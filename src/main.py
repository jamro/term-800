import argparse
import os
from rich.console import Console
from dotenv import load_dotenv
from src.shell.RemoteShell import RemoteShell
from src.ai.Assistant import Assistant
from src.chat.CmdChat import CmdChat

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

    shell = RemoteShell()

    chat = CmdChat(console, Assistant(shell, api_key))
    chat.welcome()
    if chat.connect():
        chat.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Term-800: AI Powered Sys Admin Assistant"
    )
    args = parser.parse_args()
    main(**vars(args))
