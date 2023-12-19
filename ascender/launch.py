from app import cli_app
from commands import projects, runner

cli_app.add_typer(projects.router, name="projects")