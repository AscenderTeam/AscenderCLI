from typing import Annotated
from typer import Context, Option
from ascender.logic.runner import RunnerLogic
from rich.console import Console
from ascender.app import cli_app
from ascender.settings import IS_UNIX

console = Console()

@cli_app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def run(ctx: Context):
    runner = RunnerLogic(console=console, command=" ".join(ctx.args))
    runner.invoke()

@cli_app.command()
def install(packages: list[str], no_cache: Annotated[bool, Option] = Option(False, "--no-cache", "-nc", help="Do not use cache while installing packages", show_default=False)):
    runner = RunnerLogic(console=console, command=f"pip3 install {' '.join(packages)}" if IS_UNIX else f"pip install {' '.join(packages)}")
    runner.command += " --no-cache" if no_cache else ""
    console.print(f"[cyan]Installing packages: {', '.join(packages)}[/cyan]")
    
    _output = runner.invoke_clean()

    if not _output:
        return
    
    if _output.returncode != 0:
        
        console.print(f"[red]Cannot install packages: {', '.join(packages)}[/red]")
        return
    
    console.print(f"[green]Packages installed successfully: {', '.join(packages)}[/green]")

@cli_app.command()
def uninstall(packages: list[str]):
    runner = RunnerLogic(console=console, command=f"pip3 uninstall {' '.join(packages)}" if IS_UNIX else f"pip uninstall {' '.join(packages)}")
    console.print(f"[cyan]Uninstalling packages: {', '.join(packages)}[/cyan]")
    
    _output = runner.invoke_clean()

    if not _output:
        return
    
    if _output.returncode != 0:
        
        console.print(f"[red]Cannot uninstall packages: {', '.join(packages)}[/red]")
        return
    
    console.print(f"[green]Packages uninstalled successfully: {', '.join(packages)}[/green]")