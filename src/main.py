import argparse
import os
from rich.console import Console
from dotenv import load_dotenv
from src.Conversation import Conversation
from src.TokenPricing import TokenPricing

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Chat with OpenAI using argparse and Rich."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="The prompt to send to OpenAI",
        default="Hello, how do you feel today?",
    )
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(
            "[bold red]Error:[/bold red] OPENAI_API_KEY not set in .env file",
            style="bold red",
        )
        return None

    def get_feeling():
        console.print("[dim]Reflecting on my feelings...[/dim]")
        return "Assistant feels focused!"

    tokenPricing = TokenPricing()

    conversation = Conversation(
        api_key, system_message="You are assistant with feelings"
    )
    conversation.add_function(
        "get_feeling", "Get the feeling of assistant", logic=get_feeling
    )

    console.print(f"[bold cyan]Sending prompt to OpenAI:[/bold cyan] {args.prompt}")
    console.print(conversation.ask(args.prompt))
    console.print("[bold cyan]Sending prompt to OpenAI:[/bold cyan] Say that in Polish")
    console.print(conversation.ask("Say that in Polish"))
    cost = tokenPricing.get_total_cost(conversation.token_stats)
    console.print(f"[bold red]Total cost: ${cost:.5f} [/bold red]")


if __name__ == "__main__":
    main()
