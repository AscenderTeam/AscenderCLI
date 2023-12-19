from ascender.app import cli_app
from ascender.commands import projects, runner

cli_app.add_typer(projects.router, name="projects")