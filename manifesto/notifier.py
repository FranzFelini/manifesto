import shutil
import getpass
from manifesto.config import Config
from manifesto.github import GitHubClient
from manifesto.email import EmailSender
from manifesto.email.templates import get_template, BuilderEmailTemplate
from manifesto.email.templates.custom import CustomEmailTemplate, print_placeholder_help
from manifesto.email.templates.basic import BasicEmailTemplate
from manifesto.validator import PRValidator


class Notifier:
    def __init__(self):
        self.config = Config()

    def setup(self):
        print("\n=== Manifesto Setup ===\n")

        github_token = getpass.getpass("Enter your GitHub Personal Access Token: ").strip()

        client = GitHubClient(github_token)
        if not client.verify_token():
            print("Error: Invalid GitHub token")
            return

        self.config.save_github_token(github_token)
        print("✓ GitHub token saved\n")

        email = input("Enter your Gmail address: ").strip()
        app_password = getpass.getpass("Enter your Gmail App Password: ").strip()

        self.config.save_email_credentials(email, app_password)
        print("✓ Email credentials saved\n")

        print("Enter recipient email addresses (one per line, empty line to finish):")
        recipients = []
        while True:
            recipient = input("> ").strip()
            if not recipient:
                break
            recipients.append(recipient)

        if recipients:
            self.config.save_recipients(recipients)
            print(f"✓ Saved {len(recipients)} recipient(s)\n")

        self.configure_branches()
        self.configure_template()

        print("Setup complete!")

    def configure_branches(self):
        print("\n=== Branch Configuration ===\n")

        current = self.config.get_branches()
        print(f"Current branches: {', '.join(current)}")
        print("Enter branch names to watch (one per line, empty line to finish).")
        print("Leave blank to keep current.\n")

        branches = []
        while True:
            branch = input("> ").strip()
            if not branch:
                break
            branches.append(branch)

        if branches:
            self.config.save_branches(branches)
            print(f"✓ Watching {len(branches)} branch(es): {', '.join(branches)}")
        else:
            print(f"✓ Keeping: {', '.join(current)}")

    def configure_template(self):
        print("\n=== Template Configuration ===\n")
        print("Choose a template type:")
        print("  1. Basic    - Default HTML template")
        print("  2. Builder  - Pick and choose components interactively")
        print("  3. Import   - Use your own HTML file\n")

        choice = input("Enter choice (1-3): ").strip()

        if choice == "2":
            template = BuilderEmailTemplate.configure()
            self.config.save_template_preference("builder", template.selected)
            print(
                f"\n✓ Builder template saved ({len(template.selected)} components selected)"
            )

        elif choice == "3":
            print_placeholder_help()
            path = input("Enter path to your HTML template file: ").strip()
            dest = self.config.get_custom_template_path()
            try:
                shutil.copy(path, dest)
                self.config.save_template_preference("custom")
                print(f"✓ Template imported to {dest}")
            except FileNotFoundError:
                print(f"Error: File not found: {path}")
            except Exception as e:
                print(f"Error importing template: {e}")

        else:
            self.config.save_template_preference("basic")
            print("✓ Basic template selected")

    def notify(self, pr_number: int):
        github_token = self.config.get_github_token()
        if not github_token:
            print("Error: GitHub token not configured. Run 'manifesto setup' first.")
            return

        email, password = self.config.get_email_credentials()
        if not email or not password:
            print(
                "Error: Email credentials not configured. Run 'manifesto setup' first."
            )
            return

        client = GitHubClient(github_token)
        repo_info = client.get_current_repo_info()

        if not repo_info:
            print("Error: Not in a git repository or no GitHub remote found")
            return

        owner, repo = repo_info
        pr_data = client.get_pr(owner, repo, pr_number)

        if not pr_data:
            print(f"Error: Could not fetch PR #{pr_number}")
            return

        branches = self.config.get_branches()
        validator = PRValidator(set(branches))
        if not validator.should_notify(pr_data):
            print(f"PR #{pr_number} does not target watched branches ({', '.join(branches)}). Skipping.")
            return

        template = get_template(self.config)
        subject, body = template.generate(pr_data)

        print("\n" + "=" * 60)
        print("EMAIL PREVIEW")
        print("=" * 60)
        print(f"Subject: {subject}")
        print(f"From: {email}")
        print(f"\nBranch: {pr_data['head']['ref']} → {pr_data['base']['ref']}")
        print(f"Author: {pr_data['user']['login']}")
        print(f"Title: {pr_data['title']}")
        print("=" * 60)

        input("\nPress Enter to continue...")

        recipients = self.config.get_recipients()
        if not recipients:
            print("\nNo recipients configured.")
            return

        print("\nAvailable recipients:")
        for i, recipient in enumerate(recipients, 1):
            print(f"{i}. {recipient}")

        choice = input("\nSelect recipient number (or 'all'): ").strip().lower()

        sender = EmailSender(email, password)

        if choice == "all":
            for recipient in recipients:
                if sender.send(recipient, subject, body):
                    print(f"✓ Email sent to {recipient}")
                else:
                    print(f"✗ Failed to send to {recipient}")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(recipients):
                    recipient = recipients[idx]
                    if sender.send(recipient, subject, body):
                        print(f"✓ Email sent to {recipient}")
                    else:
                        print(f"✗ Failed to send to {recipient}")
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
