"""
ClaudePersonalAssistant - A personal assistant agent that:
1. Checks your Notion ToDo list for items due within 5 days
2. Checks your Dex CRM for contacts in your Keep In Touch list
3. Sends a nicely formatted reminder email via SMTP
"""

import asyncio
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)

load_dotenv()


@tool(
    "send_email",
    "Send an email via SMTP. Use this to send reminder emails with formatted content.",
    {
        "to": str,
        "subject": str,
        "body_html": str,
    },
)
async def send_email(args: dict[str, Any]) -> dict[str, Any]:
    """Send an email using SMTP configuration from environment variables."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL", smtp_user)

    if not all([smtp_host, smtp_user, smtp_password]):
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Error: SMTP configuration incomplete. Please set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD environment variables.",
                }
            ],
            "is_error": True,
        }

    to_email = args["to"]
    subject = args["subject"]
    body_html = args["body_html"]

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        html_part = MIMEText(body_html, "html")
        msg.attach(html_part)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Email sent successfully to {to_email} with subject: {subject}",
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Failed to send email: {str(e)}"}],
            "is_error": True,
        }


def get_agent_prompt() -> str:
    """Generate the prompt for the personal assistant agent."""
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    if not recipient_email:
        raise ValueError("RECIPIENT_EMAIL environment variable is required")

    today = datetime.now().strftime("%Y-%m-%d")

    return f"""You are a personal assistant helping the user stay on top of their tasks and relationships.

Today's date is: {today}

Your job is to:

1. **Check Notion ToDo List**:
   - Search the user's Notion workspace for their ToDo/Tasks database
   - Find all tasks that are due within the next 5 days (from today: {today})
   - Note the task name, due date, and any relevant details

2. **Check Dex CRM Keep In Touch List**:
   - Search the Dex CRM for contacts that need attention
   - Look for contacts in the "Keep In Touch" list or those with upcoming reminders
   - Note contact names and any relevant context about why to reach out

3. **Send a Reminder Email**:
   - Compose a nicely formatted HTML email summarizing:
     - Upcoming tasks from Notion (organized by due date)
     - Contacts to reach out to from Dex CRM
   - Send the email to: {recipient_email}
   - Use a clear, professional format with sections and bullet points
   - Subject line should include today's date

Start by searching Notion for the ToDo database, then check Dex CRM, and finally compose and send the email.

If you encounter any issues accessing Notion or Dex, include what information you were able to gather and note what couldn't be accessed."""


async def run_assistant() -> None:
    """Run the personal assistant agent."""
    print("Starting ClaudePersonalAssistant...")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    email_server = create_sdk_mcp_server(
        name="email", version="1.0.0", tools=[send_email]
    )

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful personal assistant that checks tasks and contacts, then sends reminder emails.",
        mcp_servers={"email": email_server},
        allowed_tools=[
            "mcp__email__send_email",
            "mcp__plugin_Notion_notion__notion-search",
            "mcp__plugin_Notion_notion__notion-fetch",
            "mcp__dex__search_contacts_full_text",
            "mcp__dex__get_contact_details",
            "mcp__dex__get_contact_reminders",
        ],
        permission_mode="bypassPermissions",
    )

    prompt = get_agent_prompt()

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"\n{block.text}")
            elif isinstance(message, ResultMessage):
                print("\n" + "-" * 50)
                if message.is_error:
                    print(f"Agent completed with error")
                else:
                    print(f"Agent completed successfully")
                print(f"Duration: {message.duration_ms / 1000:.2f}s")
                if message.total_cost_usd:
                    print(f"Cost: ${message.total_cost_usd:.4f}")
    except Exception as e:
        print(f"\nError running assistant: {e}")
        raise


def main() -> None:
    """Entry point for the personal assistant."""
    required_vars = ["ANTHROPIC_API_KEY", "RECIPIENT_EMAIL"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease copy .env.example to .env and fill in your values.")
        return

    asyncio.run(run_assistant())


if __name__ == "__main__":
    main()
