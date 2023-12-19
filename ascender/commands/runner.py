from logic.runner import RunnerLogic
from rich.console import Console
from app import cli_app

console = Console()

@cli_app.command()
def run(commands: list[str]):
    runner = RunnerLogic(console=console, command=" ".join(commands))
    runner.invoke()