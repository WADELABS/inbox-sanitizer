# Inbox Sanitizer

A tool that automatically cleans up your Gmail inbox by archiving messages that match rules you define.

## What it does

- Connects to your Gmail account
- Reads messages in your inbox
- Applies rules to decide which messages to archive
- Archives them automatically (or shows you what would be archived)

## Why use it

Email overload is real. Newsletters, notifications, and old messages pile up. This tool runs in the background and keeps your inbox focused on messages that actually matter.

## Setup

### 1. Get Google API credentials

You need to enable the Gmail API for your account:

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable the Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the JSON file and save it as `credentials.json` in this folder

### 2. Install

```bash
# Clone the repository
git clone https://github.com/WADELABS/inbox-sanitizer.git
cd inbox-sanitizer

# Install dependencies
pip install -r requirements.txt

# Or install the package itself
pip install -e .
```

### 3. Authenticate

```bash
inbox-sanitizer auth
```

This will open a browser window asking you to log into Google and grant access. After you approve, it saves a token so you don't have to do this again.

## Usage

### See what would be archived (without changing anything)

```bash
inbox-sanitizer check
```

This shows you which messages match your rules but doesn't modify anything.

### Actually archive messages

```bash
inbox-sanitizer clean
```

This archives all messages that match your rules.

### Run continuously

```bash
inbox-sanitizer daemon
```

This checks your inbox every hour and archives matching messages automatically.

### Options

```bash
# Process more messages at once
inbox-sanitizer clean --max 200

# Run daemon every 30 minutes instead of every hour
inbox-sanitizer daemon --interval 30

# Use a different filter config file
inbox-sanitizer clean --config my-filters.yaml
```

## Filter Rules

Edit `config/filters.yaml` to control what gets archived:

```yaml
# Always keep emails from these domains
whitelist:
  - "@company.com"
  - "@important-client.org"

# Always archive emails from these domains
blacklist:
  - "@marketing.com"
  - "newsletter@"

# Archive messages containing these words
newsletter_patterns:
  - "unsubscribe"
  - "newsletter"
  - "no-reply"

# Archive messages older than 30 days
max_age_days: 30
```

## How it works

1. The tool authenticates with Google using OAuth2
2. It searches your inbox for messages
3. For each message, it checks sender, subject, and age against your rules
4. Messages that match rules are archived (removed from inbox but still accessible in All Mail)
5. The daemon runs this process automatically at set intervals

## Privacy

- All processing happens on your machine
- Your email data never leaves your computer
- The only external communication is with Google's Gmail API
- The token file stores your authentication locally

## Commands reference

| Command | Description |
|---------|-------------|
| `auth` | Connect to Gmail (run once) |
| `test-auth` | Test connection and show account info |
| `check` | Preview what would be archived |
| `clean` | Actually archive messages |
| `daemon` | Run continuously |

## Authentication

### First-Time Setup

1. **Get Gmail API Credentials:**
   ```bash
   # 1. Go to https://console.cloud.google.com/
   # 2. Create a new project or select existing
   # 3. Enable Gmail API
   # 4. Create OAuth 2.0 Client ID credentials
   # 5. Download credentials.json to project root
   ```

2. **Authenticate:**
   ```bash
   inbox-sanitizer auth
   ```
   This will open a browser for OAuth consent. After approval, credentials are saved to `token.pickle`.

3. **Test Connection:**
   ```bash
   inbox-sanitizer test-auth
   ```
   Output:
   ```
   ✓ Successfully connected to Gmail
     Email: your-email@gmail.com
     Total messages: 1234
   ```

### Token Management

- **Tokens are automatically refreshed** when expired
- **Token stored in:** `token.pickle` (don't commit this!)
- **Logout/Switch accounts:**
  ```python
  from src.auth import revoke_credentials
  revoke_credentials()
  ```

### Troubleshooting

**"Missing credentials.json" error:**
- Download OAuth2 credentials from Google Cloud Console
- Save as `credentials.json` in project root

**Token refresh failures:**
- Run `inbox-sanitizer auth` to re-authenticate
- Check internet connection and API quota

**Permission errors:**
- Ensure Gmail API scope includes `gmail.modify`
- Re-authenticate if scope changed

## Requirements

- Python 3.6 or higher
- A Google account with Gmail
- Gmail API enabled in Google Cloud Console
