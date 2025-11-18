import base64
import os
from pathlib import Path
from dotenv import load_dotenv

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

CLIENT_SECRET_FILE = BASE_DIR / os.getenv("GMAIL_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = BASE_DIR / "token_gmail.json"


def _get_gmail_service():
    """Initialise le client Gmail avec OAuth."""
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def _extract_body_from_payload(payload: dict) -> str:
    """Récupère le texte brut du corps de l'email."""
    body = ""

    # Corps simple
    if "data" in payload.get("body", {}):
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        return body

    # Emails multipart
    for part in payload.get("parts", []):
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain" and "data" in part.get("body", {}):
            body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
            return body

    return body


def get_email_data(n: int = 10):
    """Lit les n derniers emails Gmail via OAuth utilisateur."""
    service = _get_gmail_service()

    results = service.users().messages().list(userId="me", maxResults=n).execute()
    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        message = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        subject = next((h["value"] for h in headers if h.get("name") == "Subject"), "")
        body = _extract_body_from_payload(payload)

        emails.append({"subject": subject, "body": body})

    return emails
