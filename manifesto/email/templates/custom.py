from pathlib import Path
from typing import Dict, Any
from manifesto.email.templates.base import EmailTemplate


PLACEHOLDERS = {
    "{number}": "PR number",
    "{title}": "PR title",
    "{author}": "PR author username",
    "{head_branch}": "Source branch",
    "{base_branch}": "Target branch",
    "{state}": "PR state (OPEN/CLOSED/MERGED)",
    "{description}": "PR body/description",
    "{url}": "Link to the PR on GitHub",
    "{repo}": "Repository full name (owner/repo)",
}


def print_placeholder_help():
    print("\nAvailable placeholders for your template:")
    for placeholder, description in PLACEHOLDERS.items():
        print(f"  {placeholder:<16} {description}")
    print()


class CustomEmailTemplate(EmailTemplate):
    def __init__(self, template_path: Path):
        self.template_path = template_path

    def generate(self, pr_data: Dict[str, Any]) -> tuple[str, str]:
        with open(self.template_path, "r", encoding="utf-8") as f:
            template = f.read()

        subject = f"PR #{pr_data['number']}: {pr_data['title']}"
        body = template.format_map(
            {
                "number": pr_data["number"],
                "title": pr_data["title"],
                "author": pr_data["user"]["login"],
                "head_branch": pr_data["head"]["ref"],
                "base_branch": pr_data["base"]["ref"],
                "state": pr_data["state"].upper(),
                "description": pr_data.get("body", "No description provided."),
                "url": pr_data["html_url"],
                "repo": pr_data["base"]["repo"]["full_name"],
            }
        )

        return subject, body
