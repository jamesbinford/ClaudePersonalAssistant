"""
Google Calendar integration for ClaudePersonalAssistant.

To set up:
1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable the Google Calendar API
4. Go to Credentials > Create Credentials > OAuth client ID
5. Choose "Desktop app" as application type
6. Download the JSON file and save as 'credentials.json' in this directory
7. First run will open a browser for authentication
"""

import os
from datetime import datetime, timedelta
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying scopes, delete token.json
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")


def get_calendar_service():
    """Get authenticated Google Calendar service."""
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    "Please set up Google Calendar API credentials. "
                    "See calendar_integration.py for instructions."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_upcoming_events(days: int = 5) -> list[dict[str, Any]]:
    """
    Fetch calendar events for the next N days.

    Returns a list of events with: summary, start, end, location, description
    """
    try:
        service = get_calendar_service()

        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=days)).isoformat() + "Z"

        # Get events from primary calendar
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=50,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        # Format events for the agent
        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))

            formatted_events.append({
                "summary": event.get("summary", "No title"),
                "start": start,
                "end": end,
                "location": event.get("location", ""),
                "description": event.get("description", ""),
                "hangout_link": event.get("hangoutLink", ""),
            })

        return formatted_events

    except HttpError as error:
        print(f"Google Calendar API error: {error}")
        return []
    except FileNotFoundError as e:
        print(f"Calendar setup required: {e}")
        return []
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []


def format_events_for_prompt(events: list[dict[str, Any]]) -> str:
    """Format events as a string for the agent prompt."""
    if not events:
        return "No calendar events found for the next 5 days (or calendar not configured)."

    lines = []
    for event in events:
        start = event["start"]
        # Parse and format the date/time
        if "T" in start:
            # DateTime format
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            date_str = dt.strftime("%a %b %d, %I:%M %p")
        else:
            # Date only (all-day event)
            dt = datetime.fromisoformat(start)
            date_str = dt.strftime("%a %b %d") + " (all day)"

        line = f"- {date_str}: {event['summary']}"
        if event["location"]:
            line += f" @ {event['location']}"
        lines.append(line)

    return "\n".join(lines)


if __name__ == "__main__":
    # Test the calendar integration
    print("Testing Google Calendar integration...")
    events = get_upcoming_events(5)
    if events:
        print(f"\nFound {len(events)} events:")
        print(format_events_for_prompt(events))
    else:
        print("\nNo events found or calendar not configured.")
