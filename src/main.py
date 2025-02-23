import argparse
from openai import OpenAI
import os
from rich.console import Console
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()


def ask_openai(prompt):
    """Call OpenAI API with a given prompt."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(
            "[bold red]Error:[/bold red] OPENAI_API_KEY not set in .env file",
            style="bold red",
        )
        return None

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(
        description="Chat with OpenAI using argparse and Rich."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="The prompt to send to OpenAI",
        default="Hello, how are you?",
    )
    args = parser.parse_args()

    console.print(f"[bold cyan]Sending prompt to OpenAI:[/bold cyan] {args.prompt}")
    result = ask_openai(args.prompt)

    if result:
        console.print("[bold green]Response:[/bold green]", result)


if __name__ == "__main__":
    main()
