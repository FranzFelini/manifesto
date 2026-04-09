# Manifesto

Automated email notifications for GitHub pull requests. Supports professional release notifications with auto-detected environment, migration detection, downtime windows, and multi-language output.

## Installation

```bash
pip install manifesto-nt
```

Or from source:

```bash
pip install -e .
```

---

## Commands

### `manifesto setup`

Initial configuration wizard. Run once before using any other command.

Prompts for:
- GitHub Personal Access Token (with `repo` scope)
- Gmail address and App Password
- Recipient email addresses
- Display name for email signature
- Watched branches
- Email template preference

```bash
manifesto setup
```

---

### `manifesto notify <pr-number> [--repo owner/repo]`

Fetch a pull request and send an email notification.

```bash
# Auto-detect repo from current git directory
manifesto notify 42

# Specify repo explicitly (run from anywhere)
manifesto notify 42 --repo FranzFelini/manifesto
```

At the start of every `notify` run you will be asked to confirm the **language** (`en` / `bs`). Your choice is saved for next time.

The flow:
1. Language selection (English or Bosnian/Croatian/Montenegrin/Serbian)
2. Fetches PR details from GitHub
3. Checks if PR targets a watched branch
4. If **release template** is active — collects release information interactively:
   - Release version (fetched from latest GitHub release as default)
   - Downtime window (start/end HH:MM)
   - Migrations (auto-detected from PR file diff)
   - Database seeds (auto-detected)
   - `.env` changes (auto-detected)
   - Deploy steps
   - Additional notes / changelog
   - Special note (NAPOMENA)
5. Displays full email preview in terminal
6. Prompts to add extra one-off recipients (not saved to config)
7. Select recipient(s) and send

---

### `manifesto branches`

Configure which target branches trigger notifications. PRs targeting branches not on this list are skipped.

```bash
manifesto branches
```

Defaults: `stg`, `staging`, `dev`, `development`

---

### `manifesto template`

Choose the email template used for notifications.

```bash
manifesto template
```

Options:

| # | Name | Description |
|---|------|-------------|
| 1 | Basic | Default HTML template with PR metadata |
| 2 | Builder | Pick and choose which PR fields to include |
| 3 | Import | Use your own HTML file with placeholders |
| 4 | Release | Interactive release notification with downtime, version, migrations, etc. |

**Import template placeholders:**

| Placeholder | Value |
|-------------|-------|
| `{number}` | PR number |
| `{title}` | PR title |
| `{author}` | PR author username |
| `{head_branch}` | Source branch |
| `{base_branch}` | Target branch |
| `{state}` | PR state (OPEN/CLOSED/MERGED) |
| `{description}` | PR body/description |
| `{url}` | Link to the PR on GitHub |
| `{repo}` | Repository full name (owner/repo) |

---

### `manifesto -v` / `manifesto --version`

Print the installed version.

```bash
manifesto --version
```

---

## Release Template

The release template (`manifesto template` → option 4) generates a professional release notification email modelled after standard deployment communications.

**Environment is auto-detected from the PR base branch:**

| Base branch | Detected environment |
|-------------|----------------------|
| `stg`, `staging` | staging |
| `main`, `master`, `prod`, `production` | production |
| `dev`, `development` | development |
| other | branch name as-is |

**Migration & seed detection** scans the PR file diff automatically and pre-fills the defaults — you can confirm or override.

**Language** switches all static email text:
- `en` — English
- `bs` — Bosnian / Croatian / Montenegrin / Serbian

---

## Requirements

- Python 3.8+
- Gmail account with [App Password](https://support.google.com/accounts/answer/185833) enabled
- GitHub Personal Access Token with `repo` scope

---

## Configuration files

Stored in `~/.manifesto/`:

| File | Contents |
|------|----------|
| `.env` | GitHub token, Gmail address and password |
| `config.json` | Recipients, template preference, watched branches, language, signature, last version |
| `template.html` | Custom imported template (if applicable) |
