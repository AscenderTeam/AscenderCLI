import os
from typing import Optional
from typer import Typer, Option
from rich.console import Console
from rich.table import Table
from rich.style import Style

from ascender.logic.projects import InstallationMasterLogic
from ascender.logic.versions import VersionsLogic

router = Typer(name="projects", add_completion=True)
console = Console()

@router.command()
def new(name: str = Option(help="The name of the project to create. (Will create directory by passed name)", prompt=True), version: Optional[str] = Option(None, "-v", "--version")):
    installation_dir = f"{os.getcwd()}/{name}"
    installation_master = InstallationMasterLogic(console, installation_dir)
    version_manager = VersionsLogic()
    if version:
        try:
            version_manager.get_version(version)
        except:
            console.print(f"[bold red]Error: Version {version} doesn't exist in official releases and pre-releases![/bold red]")
            return
    
    installation = installation_master.run_installation(version=version)
    
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


@router.command()
def update(version: Optional[str] = Option(None, "-v", "--version")):
    console.log("Updating Ascender Framework...")
    installation_master = InstallationMasterLogic(console, os.getcwd())
    installation_master.run_update(version)
    console.log("Successfully updated Ascender Framework!")
    console.print("""
[bold red]Ascender Framework CLI[/bold red]
[bold red]------------------------[/bold red][cyan]
   ___   _________  _______   ____
  / _ | / __/ ___/ / ___/ /  /  _/
 / __ |_\ \/ /__  / /__/ /___/ /  
/_/ |_/___/\___/  \___/____/___/  [/cyan]

[bold red]------------------------[/bold red]

[yellow]Successfully updated framework to the latest version in release notes![/yellow]
""")
    

@router.command(help="Show the list of available release and pre-release versions of Ascender Framework")
def versions(only_releases: bool = Option(default=False)):
    version_manager = VersionsLogic(only_releases)
    
    version_table = Table("ID", "VERSION NAME", "VERSION", border_style=Style(color="red"))
    
    _versions = version_manager.get_versions()

    for version in _versions:
        version_display = "[bold yellow]BETA[/bold yellow]" if version["is_beta"] else ""
        current_display = "[bold](CURRENT)[/bold]" if version["is_current"] else ""
        version_table.add_row(str(version["id"]), f"{version['name']} {current_display}", f"{version['version']} {version_display}")
    
    console.print(version_table)