import os
from typer import Typer, Option
from rich.console import Console

from ascender.logic.projects import InstallationMasterLogic

router = Typer(name="projects", add_completion=True)
console = Console()

@router.command()
def new(name: str = Option(help="The name of the project to create. (Will create directory by passed name)", prompt=True)):
    installation_dir = f"{os.getcwd()}/{name}"
    installation_master = InstallationMasterLogic(console, installation_dir)

    installation = installation_master.run_installation()
    
    if not installation:
        return
    
    console.log("Successfully installed Ascender Framework! It's available in the current directory.")
    installation_master.create_environment()
    installation_master.install_requirements()
    console.print("""
[bold red]Ascender Framework CLI[/bold red]
[bold red]------------------------[/bold red][cyan]
   ___   _________  _______   ____
  / _ | / __/ ___/ / ___/ /  /  _/
 / __ |_\ \/ /__  / /__/ /___/ /  
/_/ |_/___/\___/  \___/____/___/  [/cyan]

[bold red]------------------------[/bold red]

[yellow]Welcome to Ascender Framework! You can now start developing your project, use:[/yellow] [cyan]ascender run [ARGS][/cyan] [yellow]to start the development server.[/yellow]
""")