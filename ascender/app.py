from typer import Typer

cli_app = Typer(name="AscenderCLI", add_completion=True, help="Command guideline for AscenderCLI")

__all__ = ["cli_app"]