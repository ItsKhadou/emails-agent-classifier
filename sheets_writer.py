import gspread
import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SERVICE_ACCOUNT_FILE = BASE_DIR / os.getenv("GOOGLE_SERVICE_ACCOUNT")
SHEET_ID = os.getenv("SHEET_ID")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)


def write_to_sheet(category, subject, urgency, summary):
    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.worksheet(category)
    worksheet.append_row([subject, urgency, summary])
