import subprocess
import requests  # type: ignore
from typing import Optional, Dict, Any
from manifesto.github.helpers.verify import verify_token


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    verify_token = verify_token

    def get_pr(self, owner: str, repo: str, pr_number: int) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return None

    def get_current_repo_info(self) -> Optional[tuple[str, str]]:
        try:
            remote = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                check=True,
            )
            url = remote.stdout.strip()

            if "github.com" in url:
                parts = url.replace(".git", "").split("/")
                repo = parts[-1]
                owner = parts[-2].split(":")[-1]
                return owner, repo
        except subprocess.CalledProcessError:
            pass

        return None
