import argparse
import os
from rich.prompt import Prompt
from rich.text import Text
from rich.console import Console
from dotenv import load_dotenv
from src.shell.RemoteShell import RemoteShell
from src.ai.Assistant import Assistant
from src.chat.CmdChat import CmdChat
from src.Settings import Settings

# Initialize Rich console
console = Console(highlight=False)


def main():
    # Load environment variables
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    load_dotenv(dotenv_path=env_file)

    # Check if everything is set up properly
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(
            "[red][bold]Error: OPENAI_API_KEY not found in environment variables![/bold][/red]"
        )
        console.print()
        update_key = Prompt.ask(
            Text("Do you want to set it now and store it in .env file?"),
            choices=["y", "n"],
            default="y",
        )
        if update_key != "y":
            console.print("[red]Exiting...[/red]")
            return None

        api_key = Prompt.ask(Text("Enter your OpenAI API Key"))
        with open(env_file, "a") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        console.print("[green]API Key set successfully![/green]")
        console.print()

    settings = Settings()
    settings.save_config()
    shell = RemoteShell()
    chat = CmdChat(console, settings, Assistant(shell, settings, api_key))
    chat.welcome()
    if chat.connect():
        chat.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Term-800: AI Powered Sys Admin Assistant"
    )
    args = parser.parse_args()
    main(**vars(args))
