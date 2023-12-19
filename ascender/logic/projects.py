from pathlib import Path
from settings import FRAMEWORK_TYPES, IS_UNIX
from typing import Literal, Optional
from rich.console import Console
from rich.progress_bar import ProgressBar
from git import RemoteProgress, Repo
from virtualenv.run import cli_run

import os
import subprocess


class CloneProgress(RemoteProgress):
    progress_bar: ProgressBar

    def update(self, op_code: int, cur_count: str | float, max_count: Optional[str | float] = None, message: str = ''):
        if max_count:
            progress = (cur_count / max_count) * 100
            
            self.progress_bar.update(progress)
            print(f"Progress: {progress:.2f}%", end='\r')
    


class InstallationMasterLogic:
    def __init__(self, 
                console: Console,
                installation_dir: Optional[str] = None,
                framework_type: Literal["standard"] = "standard") -> None:
        self.installation_dir = os.getcwd() if not installation_dir else installation_dir
        self.framework_type = framework_type
        self.console = console
    
    def run_installation(self, safe_mode: bool = True) -> bool:
        _project = Path(self.installation_dir)
        
        # Does project exist or not
        if _project.exists():
            self.console.print(f"[bold red]Fatal error: Cannot create project[/bold red]")
            self.console.log(f"Project with name {self.installation_dir} already exists!")
            return False
        
        self.console.print(f"[yellow]Installing Ascender Framework to [/yellow] [cyan]{self.installation_dir}[cyan]")
        
        # Set progress
        CloneProgress.progress_bar = ProgressBar()
        project = Repo.clone_from(FRAMEWORK_TYPES[self.framework_type], self.installation_dir, progress=CloneProgress(), allow_unsafe_options=(not safe_mode))
        project.delete_remote("origin")
        return True
    
    def create_environment(self, name: str = ".asc_venv"):
        # Create virtual environment
        self.console.print(f"[yellow]Starting to create virtual environment at[/yellow] [cyan]{self.installation_dir}/{name}[cyan]")
        cli_run([f"{self.installation_dir}/{name}"])
    
    def install_requirements(self, name: str = ".asc_venv"):
        # Install requirements
        if IS_UNIX:
            subprocess.run(f"source {self.installation_dir}/{name}/bin/activate && pip3 install -r {self.installation_dir}/requirements.txt", shell=True)
            return
        subprocess.run(f". {self.installation_dir}/{name}/bin/activate && pip install -r {self.installation_dir}/requirements.txt", shell=True)
    