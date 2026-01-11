# ClaudePersonalAssistant

A personal assistant agent built with the Claude Agent SDK that:

1. Checks your **Notion ToDo list** for tasks due within 5 days
2. Checks your **Dex CRM** for contacts in your Keep In Touch list
3. Sends a nicely formatted **reminder email** to you via SMTP

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Anthropic API key
- Notion MCP server configured
- Dex CRM MCP server configured
- SMTP email account (Gmail, etc.)

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

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your values:
   - `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/
   - `RECIPIENT_EMAIL` - Where to send reminders
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Your email server

4. **Configure MCP servers**

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

## Gmail SMTP Setup

If using Gmail:
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: Google Account > Security > App Passwords
3. Use the app password as `SMTP_PASSWORD`

## License

MIT
