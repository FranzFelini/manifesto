import sys
from manifesto import __version__
from manifesto.notifier import Notifier


def main():
    notifier = Notifier()

    if len(sys.argv) == 2 and sys.argv[1] in ("-v", "--version"):
        print(f"manifesto v{__version__}")
        return

    if len(sys.argv) < 2:
        print("Usage:")
        print("  manifesto setup              - Initial configuration")
        print("  manifesto notify <pr-number> - Send notification for PR")
        print("  manifesto branches           - Configure watched branches")
        print("  manifesto template           - Configure email template")
        return

    command = sys.argv[1]

    if command == "setup":
        notifier.setup()
    elif command == "notify":
        if len(sys.argv) < 3:
            print("Error: PR number required")
            print("Usage: `manifesto notify <pr-number> [--repo owner/repo]`")
            return
        try:
            pr_number = int(sys.argv[2])
        except ValueError:
            print("Error: PR number must be an integer")
            return
        repo = None
        if "--repo" in sys.argv:
            idx = sys.argv.index("--repo")
            if idx + 1 >= len(sys.argv):
                print("Error: --repo requires a value (e.g. --repo owner/repo)")
                return
            repo = sys.argv[idx + 1]
        notifier.notify(pr_number, repo=repo)
    elif command == "branches":
        notifier.configure_branches()
    elif command == "template":
        notifier.configure_template()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
