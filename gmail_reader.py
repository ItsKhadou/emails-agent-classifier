import base64
import os
from pathlib import Path
from dotenv import load_dotenv

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Load .env using relative path
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

CLIENT_SECRET_FILE = BASE_DIR / os.getenv("GMAIL_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_email_data(n=10):
    """Reads the last n Gmail emails."""
    creds = None

    # Load token if exists
    token_path = BASE_DIR / "token_gmail.pkl"
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", maxResults=n).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        message = service.users().messages().get(userId="me", id=msg["id"]).execute()

        payload = message["payload"]
        headers = payload["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")

        body = ""
        if "data" in payload.get("body", {}):
            data = payload["body"]["data"]
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        elif "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain" and "data" in part["body"]:
                    data = part["body"]["data"]
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        emails.append({"subject": subject, "body": body})

    return emails