from pathlib import Path
import shutil
from ascender.logic.versions import VersionsLogic
from ascender.settings import FRAMEWORK_STABLE_LATEST_VERSION, FRAMEWORK_TYPES, IS_UNIX
from typing import Literal, Optional
from rich.console import Console
from rich.progress_bar import ProgressBar
from rich.prompt import Confirm
from git import RemoteProgress, Repo
from virtualenv.run import cli_run
from toml import load

import os
import subprocess
import requests


class CloneProgress(RemoteProgress):
    progress_bar: ProgressBar

    def update(self, op_code: int, cur_count: str | float, max_count: Optional[str | float] = None, message: str = ''):
        if max_count:
            progress = (cur_count / max_count) * 100
            
            self.progress_bar.update(progress)
            print(f"Progress: {progress:.2f}%", end='\r')
    

class UpdaterMasterLogic:
    def __init__(self, base_path: str, framework_type: Literal["standard"] = "standard") -> None:
        self.base_path = base_path
        self.framework_type = framework_type
        self.toml_path = f"{base_path}/pyproject.toml"
        self.console = Console()
    
    def is_project(self):
        """
        Check if the current directory is an AscenderFramework project or not.
        """
        directory = os.getcwd()

        if os.path.exists(f"{directory}/.asc_venv") and os.path.exists(f"{directory}/start.py") and os.path.exists(f"{directory}/core"):
            return True

    def get_version(self) -> str:
        toml_data = load(self.toml_path)
        return toml_data["tool"]["poetry"]["version"]
    
    def get_latest_version(self) -> str:
        repo_name = "AscenderTeam/AscenderFramework"
        url = f"https://api.github.com/repos/{repo_name}/releases/latest"

        response = requests.get(url)
        latest_release = response.json()

        return latest_release.get("tag_name", FRAMEWORK_STABLE_LATEST_VERSION)

    def compare_versions(self, v1: str, v2: str):
        # Removing the 'v' prefix and splitting the versions into components
        components1 = v1.lstrip('v').split('.')
        components2 = v2.lstrip('v').split('.')

        # Compare each component
        for c1, c2 in zip(components1, components2):
            # Convert components to integers for comparison
            if int(c1) < int(c2):
                return -1
            elif int(c1) > int(c2):
                return 1

        # If all components are equal, the versions are the same
        return 0

    def update(self, version: Optional[str] = None, safe_mode: bool = True) -> bool:
        if not self.is_project():
            raise Exception("Cannot recognize project directory") # TODO: Add custom exception
        
        current_version = self.get_version()
        updatable_version = version if version else self.get_latest_version()

        _version_manager = VersionsLogic()
        # Check if updatable version does exist
        try:
            version = _version_manager.get_version(updatable_version)
            if version["is_beta"]:
                confirm = Confirm(f"Version {updatable_version} is pre-release beta version and isn't tested in production environemtns. Are you sure you want to update to it?")
                _confirmation = confirm.ask()
                if not _confirmation:
                    return
                
                self.console.print(f"[bold yellow]Version {updatable_version} is pre-release version and is not tested for production yet. So use at your own risk!")

        except:
            self.console.print(f"[bold red]Error: Version {updatable_version} doesn't exist in official releases and pre-releases![/bold red]")
        
        if self.compare_versions(current_version, updatable_version) >= 0:
            if not version:
                return False

        self.console.print(f"[yellow]Updating Ascender Framework from version[/yellow] [cyan]{current_version}[/cyan] [yellow]to version[/yellow] [cyan]{updatable_version}[/cyan]...")
        # Run installation
        temp_inst = InstallationMasterLogic(self.console, f"{self.base_path}/.asc_temp", self.framework_type)
        temp_inst.run_installation(updatable_version, safe_mode)

        # Copy core directory from self.base_path/.asc_temp to self.base_path (overwrite)
        shutil.rmtree(f"{self.base_path}/core", ignore_errors=True)
        os.remove(f"{self.base_path}/pyproject.toml")

        shutil.copytree(f"{self.base_path}/.asc_temp/core", f"{self.base_path}/core", dirs_exist_ok=True)
        shutil.copyfile(f"{self.base_path}/.asc_temp/pyproject.toml", f"{self.base_path}/pyproject.toml")

        # Apply last custom updates set in update.txt
        update_dir = f"{self.base_path}/core/update.txt"
        if os.path.exists(update_dir):
            with open(update_dir, "r") as u:
                _update_contents = u.read()
                _update_contents = _update_contents.replace("[BASE_PATH]", self.base_path)
                print(_update_contents)
                exec(_update_contents)
            os.remove(update_dir)
        
        # Delete .asc_temp directory
        shutil.rmtree(f"{self.base_path}/.asc_temp")


class InstallationMasterLogic:
    def __init__(self, 
                console: Console,
                installation_dir: Optional[str] = None,
                framework_type: Literal["standard"] = "standard") -> None:
        self.installation_dir = os.getcwd() if not installation_dir else installation_dir
        self.framework_type = framework_type
        self.console = console
    
    def run_installation(self, version: Optional[str] = None, safe_mode: bool = True) -> bool:
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
        if version:
            try:
                project.git.checkout(version)
            except:
                pass

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
        subprocess.run(f". {self.installation_dir}/{name}/Scripts/activate && pip install -r {self.installation_dir}/requirements.txt", shell=True)
    
    def run_update(self, version: Optional[str] = None, safe_mode: bool = True) -> bool:
        # Set progress
        update_master = UpdaterMasterLogic(self.installation_dir, self.framework_type)
        update_master.update(version=version)