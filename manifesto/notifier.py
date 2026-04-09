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

        github_token = getpass.getpass(
            "Enter your GitHub Personal Access Token: "
        ).strip()

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

        signature = input("Enter your display name for email signature: ").strip()
        if signature:
            self.config.save_signature(signature)
            print(f"✓ Signature saved: {signature}\n")

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
        print("  3. Import   - Use your own HTML file")
        print(
            "  4. Release  - Interactive release notification (downtime, version, migrations, etc.)\n"
        )

        choice = input("Enter choice (1-4): ").strip()

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

        elif choice == "4":
            self.config.save_template_preference("release")
            print("✓ Release template selected")

        else:
            self.config.save_template_preference("basic")
            print("✓ Basic template selected")

    def _collect_release_info(
        self, pr_data: dict, client, owner: str, repo: str, language: str = "bs"
    ) -> dict:
        en = language == "en"
        print("\n=== Release Information ===\n")

        # Version
        latest = client.get_latest_release(owner, repo)
        last_saved = self.config.get_last_version()
        suggested = latest or last_saved or "v1.0.0"
        version = input(f"Release version [{suggested}]: ").strip() or suggested
        self.config.save_last_version(version)

        # Downtime
        start_time = input("Downtime start (HH:MM): ").strip()
        end_time = input("Downtime end (HH:MM): ").strip()

        # Migrations — auto-detect from PR files
        pr_files = client.get_pr_files(owner, repo, pr_data["number"])
        migration_files = [f for f in pr_files if "migrat" in f.lower()]
        if migration_files:
            print(f"\nDetected {len(migration_files)} migration file(s):")
            for f in migration_files[:5]:
                print(f"  - {f}")
            migrations_default = (
                f"{len(migration_files)} migration(s)"
                if en
                else f"{len(migration_files)}"
            )
        else:
            migrations_default = "None required" if en else "Nema potrebnih migracija"
        migrations = (
            input(f"Migrations [{migrations_default}]: ").strip() or migrations_default
        )

        # Seeds
        seed_files = [f for f in pr_files if "seed" in f.lower()]
        if seed_files:
            seeds_default = (
                f"{len(seed_files)} seed file(s)"
                if en
                else f"{len(seed_files)} seed fajlova"
            )
        else:
            seeds_default = "None required" if en else "Nema potrebnih seed-ova"
        seeds = input(f"Seeds [{seeds_default}]: ").strip() or seeds_default

        # .env
        env_files = [
            f for f in pr_files if ".env" in f.lower() or "environment" in f.lower()
        ]
        env_default = (
            ("Changes present" if env_files else "No changes")
            if en
            else ("Ima izmjena" if env_files else "Nema izmjena")
        )
        env_changes = input(f".env changes [{env_default}]: ").strip() or env_default

        # Deploy steps
        base_branch = pr_data["base"]["ref"]
        deploy_default = f"Deploy {base_branch} branch"
        print(f"\nDeploy steps (one per line, empty to finish).")
        print(f"Press Enter immediately to use default: '{deploy_default}'")
        deploy_steps = []
        while True:
            step = input("> ").strip()
            if not step:
                break
            deploy_steps.append(step)
        if not deploy_steps:
            deploy_steps = [deploy_default]

        # Additional notes
        label = "Additional notes/changelog" if en else "Dodatne napomene/changelog"
        print(f"\n{label} (one per line, empty to finish):")
        notes = []
        while True:
            note = input("> ").strip()
            if not note:
                break
            notes.append(note)

        # Special note
        note_label = (
            "NOTE (special note, or Enter to skip)"
            if en
            else "NAPOMENA (posebna napomena, ili Enter za preskok)"
        )
        napomena_raw = input(f"\n{note_label}: ").strip()
        napomena = napomena_raw if napomena_raw not in ("", "/", ".") else ""

        # Signature
        signature = self.config.get_signature() or pr_data["user"]["login"]

        return {
            "version": version,
            "start_time": start_time,
            "end_time": end_time,
            "migrations": migrations,
            "seeds": seeds,
            "env_changes": env_changes,
            "deploy_steps": deploy_steps,
            "notes": notes,
            "napomena": napomena,
            "signature": signature,
        }

    def notify(self, pr_number: int, repo: str = None):
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

        saved_lang = self.config.get_language() or "bs"
        lang_label = (
            "English" if saved_lang == "en" else "Bosnian/Croatian/Montenegrin/Serbian"
        )
        lang_input = input(f"Language [{lang_label}] (en/bs): ").strip().lower()
        if lang_input in ("en", "bs"):
            language = lang_input
            self.config.save_language(language)
        else:
            language = saved_lang

        client = GitHubClient(github_token)

        if repo:
            parts = repo.split("/")
            if len(parts) != 2 or not all(parts):
                print("Error: --repo must be in the format owner/repo")
                return
            owner, repo = parts
        else:
            repo_info = client.get_current_repo_info()
            if not repo_info:
                print("Error: Not in a git repository or no GitHub remote found.")
                print("Tip: Use --repo owner/repo to specify a repository explicitly.")
                return
            owner, repo = repo_info
        pr_data = client.get_pr(owner, repo, pr_number)

        if not pr_data:
            print(f"Error: Could not fetch PR #{pr_number}")
            return

        branches = self.config.get_branches()
        validator = PRValidator(set(branches))
        if not validator.should_notify(pr_data):
            print(
                f"PR #{pr_number} does not target watched branches ({', '.join(branches)}). Skipping."
            )
            return

        template = get_template(self.config)

        if self.config.get_template_preference().get("type") == "release":
            pr_data["_release"] = self._collect_release_info(
                pr_data, client, owner, repo, language=language
            )
            pr_data["_release"]["language"] = language

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
