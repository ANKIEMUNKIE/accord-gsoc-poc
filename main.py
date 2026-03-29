#!/usr/bin/env python3
"""
Accord Project Template Generator - Agentic Workflow POC
GSoC 2025 - Project 1: Agentic Workflow for Drafting Templates
Author: [Your Name]
"""
from dotenv import load_dotenv
load_dotenv()
import argparse
import sys
from crew import TemplateCrew
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

BANNER = """
╔═══════════════════════════════════════════════════════╗
║     Accord Project Template Generator (GSoC POC)      ║
║         Agentic Workflow with Multi-Agent AI           ║
╚═══════════════════════════════════════════════════════╝
"""

def run_interactive():
    """Interactive CLI mode — user types requirements in natural language."""
    console.print(BANNER, style="bold cyan")
    console.print("Type your template requirements below. Type 'exit' to quit.\n", style="dim")

    while True:
        try:
            user_input = console.input("[bold green]📝 Template Requirements > [/bold green]")
            if user_input.lower() in ("exit", "quit"):
                console.print("\n👋 Goodbye!", style="bold yellow")
                break
            if not user_input.strip():
                continue

            console.print("\n[bold cyan]🚀 Starting agentic workflow...[/bold cyan]\n")
            crew = TemplateCrew(user_input)
            result = crew.run()

            console.print(Panel(
                result,
                title="[bold green]✅ Generated Accord Project Template[/bold green]",
                border_style="green"
            ))

        except KeyboardInterrupt:
            console.print("\n\n👋 Interrupted. Goodbye!", style="bold yellow")
            sys.exit(0)


def run_single(requirements: str, model: str, output_dir: str):
    """Single-shot mode — pass requirements as argument."""
    console.print(BANNER, style="bold cyan")
    console.print(f"[bold]Requirements:[/bold] {requirements}")
    console.print(f"[bold]Model:[/bold] {model}")
    console.print(f"[bold]Output:[/bold] {output_dir}\n")

    console.print("[bold cyan]🚀 Starting agentic workflow...[/bold cyan]\n")
    crew = TemplateCrew(requirements, model=model, output_dir=output_dir)
    result = crew.run()

    console.print(Panel(
        result,
        title="[bold green]✅ Generated Accord Project Template[/bold green]",
        border_style="green"
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Accord Project Agentic Template Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                      # Interactive mode
  python main.py -r "NDA between two parties"        # Single shot
  python main.py -r "Late payment penalty clause" --model gpt-4o --output ./my-template
        """
    )
    parser.add_argument("-r", "--requirements", type=str, help="Template requirements in natural language")
    parser.add_argument("--model", type=str, default="groq/llama-3.3-70b-versatile", 
                        help="LLM model to use (default: groq - free!)")
    parser.add_argument("--output", type=str, default="./output", help="Output directory for generated template files")

    args = parser.parse_args()

    if args.requirements:
        run_single(args.requirements, args.model, args.output)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
