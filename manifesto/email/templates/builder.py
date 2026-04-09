from typing import Dict, Any, List
from manifesto.email.templates.base import EmailTemplate


COMPONENTS = [
    ("header", "Header", "PR Notification banner at the top"),
    ("repository", "Repository", "Repository full name"),
    ("pr_number", "PR Number", "Pull request number"),
    ("title", "Title", "PR title"),
    ("author", "Author", "PR author username"),
    ("branch", "Branch", "head → base branch"),
    ("status", "Status", "PR state (open/closed/merged)"),
    ("description", "Description", "PR body/description"),
    ("view_button", "View Button", "Link button to open the PR"),
    ("footer", "Footer", "Automated notification footer"),
]

ALL_COMPONENT_KEYS = [key for key, _, _ in COMPONENTS]


class BuilderEmailTemplate(EmailTemplate):
    def __init__(self, selected: List[str]):
        self.selected = selected

    def generate(self, pr_data: Dict[str, Any]) -> tuple[str, str]:
        subject = f"PR #{pr_data['number']}: {pr_data['title']}"

        css = """
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #0366d6; color: white; padding: 15px; border-radius: 5px; }
            .subheading { color: #586069; font-size: 14px; margin: 5px 0 0; }
            .content { background: #f6f8fa; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .field { margin: 10px 0; }
            .label { font-weight: bold; color: #586069; }
            .value { margin-left: 10px; }
            .description { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #0366d6; }
            .footer { color: #586069; font-size: 12px; margin-top: 20px; }
        </style>
        """

        sections = []

        if "header" in self.selected:
            repo = (
                pr_data["base"]["repo"]["full_name"]
                if "repository" in self.selected
                else ""
            )
            subheading = f'<p class="subheading">{repo}</p>' if repo else ""
            sections.append(
                f'<div class="header"><h2>Pull Request Notification</h2>{subheading}</div>'
            )
        elif "repository" in self.selected:
            sections.append(f'<h3>{pr_data["base"]["repo"]["full_name"]}</h3>')

        fields = []
        if "pr_number" in self.selected:
            fields.append(
                f'<div class="field"><span class="label">PR Number:</span><span class="value">#{pr_data["number"]}</span></div>'
            )
        if "title" in self.selected:
            fields.append(
                f'<div class="field"><span class="label">Title:</span><span class="value">{pr_data["title"]}</span></div>'
            )
        if "author" in self.selected:
            fields.append(
                f'<div class="field"><span class="label">Author:</span><span class="value">{pr_data["user"]["login"]}</span></div>'
            )
        if "branch" in self.selected:
            fields.append(
                f'<div class="field"><span class="label">Branch:</span><span class="value">{pr_data["head"]["ref"]} → {pr_data["base"]["ref"]}</span></div>'
            )
        if "status" in self.selected:
            fields.append(
                f'<div class="field"><span class="label">Status:</span><span class="value">{pr_data["state"].upper()}</span></div>'
            )
        if "description" in self.selected:
            body_text = pr_data.get("body", "No description provided.")
            fields.append(
                f'<div class="description"><strong>Description:</strong><p>{body_text}</p></div>'
            )
        if "view_button" in self.selected:
            fields.append(
                f'<div class="field"><a href="{pr_data["html_url"]}" style="background:#0366d6;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;display:inline-block;">View Pull Request</a></div>'
            )

        if fields:
            sections.append('<div class="content">' + "\n".join(fields) + "</div>")

        if "footer" in self.selected:
            sections.append(
                '<div class="footer">This is an automated notification from manifesto package.</div>'
            )

        body = f"""
        <html>
        <head>{css}</head>
        <body>
            <div class="container">
                {"".join(sections)}
            </div>
        </body>
        </html>
        """

        return subject, body

    @staticmethod
    def configure() -> "BuilderEmailTemplate":
        print("\n=== Template Builder ===\n")
        print("Toggle components with their number, 'done' when finished:\n")

        selected = set(ALL_COMPONENT_KEYS)

        while True:
            for i, (key, label, description) in enumerate(COMPONENTS, 1):
                mark = "x" if key in selected else " "
                print(f"  [{mark}] {i:>2}. {label:<14} - {description}")

            print()
            choice = input("Enter number to toggle, or 'done': ").strip().lower()

            if choice == "done":
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(COMPONENTS):
                    key = COMPONENTS[idx][0]
                    if key in selected:
                        selected.discard(key)
                    else:
                        selected.add(key)
                    print()
                else:
                    print("Invalid number.\n")
            except ValueError:
                print("Enter a number or 'done'.\n")

        ordered = [key for key, _, _ in COMPONENTS if key in selected]
        return BuilderEmailTemplate(ordered)
