# Manifesto

Automated email notifications for GitHub pull requests targeting staging/development branches.

## Installation

```bash
pip install -e .
```

## Setup

Run once to configure:

```bash
manifesto setup
```

This will prompt for:
- GitHub Personal Access Token (with `repo` scope)
- Gmail address and App Password
- Recipient email addresses

## Usage

From any git repository with a GitHub remote:

```bash
manifesto notify <pr-number>
```

Example:
```bash
manifesto notify 42
```

The tool will:
1. Fetch PR details from GitHub
2. Check if PR targets stg/staging/dev/development branches
3. Display email preview
4. Let you choose recipients
5. Send the notification

## Requirements

- Python 3.8+
- Gmail account with App Password enabled
- GitHub Personal Access Token

## Configuration

Settings stored in `~/.manifesto/`:
- `.env` - Credentials (GitHub token, email)
- `config.json` - Recipient list
