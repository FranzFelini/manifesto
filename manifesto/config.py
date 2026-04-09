import os
import json
from pathlib import Path
from typing import List, Optional


class Config:
    CONFIG_DIR = Path.home() / ".manifesto"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    ENV_FILE = CONFIG_DIR / ".env"

    def __init__(self):
        self.CONFIG_DIR.mkdir(exist_ok=True)

    def _secure_write(self, path: Path, content: str, mode: str = "w") -> None:
        with open(path, mode) as f:
            f.write(content)
        try:
            os.chmod(path, 0o600)  # owner read/write only
        except NotImplementedError:
            pass  # Windows — folder-level permissions apply instead

    def save_github_token(self, token: str) -> None:
        self._secure_write(self.ENV_FILE, f"GITHUB_TOKEN={token}\n")

    def get_github_token(self) -> Optional[str]:
        if not self.ENV_FILE.exists():
            return None
        with open(self.ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip()
        return None

    def save_email_credentials(self, email: str, app_password: str) -> None:
        self._secure_write(
            self.ENV_FILE,
            f"EMAIL_ADDRESS={email}\nEMAIL_PASSWORD={app_password}\n",
            mode="a",
        )

    def get_email_credentials(self) -> tuple[Optional[str], Optional[str]]:
        if not self.ENV_FILE.exists():
            return None, None

        email, password = None, None
        with open(self.ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("EMAIL_ADDRESS="):
                    email = line.split("=", 1)[1].strip()
                elif line.startswith("EMAIL_PASSWORD="):
                    password = line.split("=", 1)[1].strip()
        return email, password

    def _read_config(self) -> dict:
        if not self.CONFIG_FILE.exists():
            return {}
        with open(self.CONFIG_FILE, "r") as f:
            return json.load(f)

    def _write_config(self, data: dict) -> None:
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def save_recipients(self, recipients: List[str]) -> None:
        data = self._read_config()
        data["recipients"] = recipients
        self._write_config(data)

    def get_recipients(self) -> List[str]:
        return self._read_config().get("recipients", [])

    def save_template_preference(
        self, template_type: str, components: List[str] = None
    ) -> None:
        data = self._read_config()
        data["template"] = {"type": template_type}
        if components is not None:
            data["template"]["components"] = components
        self._write_config(data)

    def get_template_preference(self) -> dict:
        return self._read_config().get("template", {"type": "basic"})

    def get_custom_template_path(self) -> "Path":
        return self.CONFIG_DIR / "template.html"

    def save_branches(self, branches: List[str]) -> None:
        data = self._read_config()
        data["branches"] = branches
        self._write_config(data)

    def get_branches(self) -> List[str]:
        return self._read_config().get("branches", ["stg", "staging", "dev", "development"])

    def save_signature(self, signature: str) -> None:
        data = self._read_config()
        data["signature"] = signature
        self._write_config(data)

    def get_signature(self) -> Optional[str]:
        return self._read_config().get("signature")

    def save_last_version(self, version: str) -> None:
        data = self._read_config()
        data["last_version"] = version
        self._write_config(data)

    def get_last_version(self) -> Optional[str]:
        return self._read_config().get("last_version")

    def save_language(self, language: str) -> None:
        data = self._read_config()
        data["language"] = language
        self._write_config(data)

    def get_language(self) -> Optional[str]:
        return self._read_config().get("language")
