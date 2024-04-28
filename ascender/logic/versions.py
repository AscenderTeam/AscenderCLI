from toml import load

import os
import requests


class VersionsLogic:
    def __init__(self, only_releases: bool = False) -> None:
        self.only_releases = only_releases
        self.toml_path = f"{os.getcwd()}/pyproject.toml"
    
    def is_project(self):
        """
        Check if the current directory is an AscenderFramework project or not.
        """
        directory = os.getcwd()

        if os.path.exists(f"{directory}/.asc_venv") and os.path.exists(f"{directory}/start.py") and os.path.exists(f"{directory}/core"):
            return True

    def get_versions(self):
        repo_name = "AscenderTeam/AscenderFramework"
        url = f"https://api.github.com/repos/{repo_name}/releases"

        response = requests.get(url)
        releases = response.json()

        output_list = []
        for release in releases:
            payload = {"id": release["id"], "name": f"AscenderFramework@{release['name']}", "is_beta": release["prerelease"], "version": release["tag_name"], "is_current": self.is_project() and self.get_project_version() == release["tag_name"]}
            if release["draft"]:
                continue
            
            if self.only_releases and not release["prerelease"]:
                output_list.append(payload)
                continue
            output_list.append(payload)
        
        return output_list
    
    def get_version(self, version: str):
        repo_name = "AscenderTeam/AscenderFramework"
        url = f"https://api.github.com/repos/{repo_name}/releases/tags/{version}"

        response = requests.get(url)
        release = response.json()

        return {"id": release["id"], "name": f"AscenderFramework@{release['name']}", "is_beta": release["prerelease"], "version": release["tag_name"], "is_current": self.is_project() and self.get_project_version() == release["tag_name"]}

    def get_project_version(self):
        toml_data = load(self.toml_path)
        return "v" + toml_data["tool"]["poetry"]["version"]

    def get_latest(self):
        repo_name = "AscenderTeam/AscenderFramework"
        url = f"https://api.github.com/repos/{repo_name}/releases/latest"

        response = requests.get(url)
        release = response.json()

        return {"id": release["id"], "name": f"AscenderFramework@{release['name']}", "is_beta": release["prerelease"], "version": release["tag_name"], "is_current": self.is_project() and self.get_project_version() == release["tag_name"]}
