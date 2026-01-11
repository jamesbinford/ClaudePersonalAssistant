# ClaudePersonalAssistant

A personal assistant agent built with the Claude Agent SDK that:

1. Checks your **Notion ToDo list** for tasks due within 5 days
2. Checks your **Dex CRM** for contacts in your Keep In Touch list
3. Sends a nicely formatted **reminder email** to you via SMTP

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [Docker](https://docs.docker.com/get-docker/) (for local email server)
- Anthropic API key
- Notion MCP server configured
- Dex CRM MCP server configured

## Setup

1. **Clone the repository**
   ```bash
   git clone git@github.com:jamesbinford/ClaudePersonalAssistant.git
   cd ClaudePersonalAssistant
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Start the local email server**
   ```bash
   docker compose up -d
   ```
   This starts [Mailpit](https://mailpit.axllent.org/) which catches emails locally and can relay them to Gmail.

   - **Web UI**: http://localhost:8025 (view caught emails)
   - **SMTP**: localhost:1025

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your values:
   - `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/
   - `RECIPIENT_EMAIL` - Where to send reminders
   - `RELAY_USER`, `RELAY_PASSWORD` - Gmail credentials to actually send emails

5. **Configure MCP servers**

   Ensure your Notion and Dex MCP servers are configured in your Claude Code settings.

## Usage

Run the assistant:

```bash
uv run python main.py
```

The agent will:
1. Search your Notion workspace for ToDo items
2. Query Dex CRM for Keep In Touch contacts
3. Compose and send a formatted reminder email

## Email Configuration

### Local Testing (default)
Emails are caught by Mailpit. View them at http://localhost:8025

### Actually Send Emails
Configure Gmail relay in your `.env`:
```bash
RELAY_HOST=smtp.gmail.com
RELAY_USER=your_email@gmail.com
RELAY_PASSWORD=your_app_password
RELAY_ALL=true
```

### Gmail App Password
1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account > Security > App Passwords
3. Generate a password for "Mail"
4. Use that as `RELAY_PASSWORD`

## Docker Commands

```bash
# Start Mailpit
docker compose up -d

# View logs
docker compose logs -f mailpit

# Stop
docker compose down

# Stop and remove data
docker compose down -v
```

## License

MIT
