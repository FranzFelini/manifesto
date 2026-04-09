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
            print("Usage: `manifesto notify <pr-number>`")
            return
        try:
            pr_number = int(sys.argv[2])
            notifier.notify(pr_number)
        except ValueError:
            print("Error: PR number must be an integer")
    elif command == "branches":
        notifier.configure_branches()
    elif command == "template":
        notifier.configure_template()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
