import gspread
import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SERVICE_ACCOUNT_FILE = BASE_DIR / os.getenv("GOOGLE_SERVICE_ACCOUNT")
SHEET_ID = os.getenv("SHEET_ID")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(str(SERVICE_ACCOUNT_FILE), scopes=SCOPES)
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID)

WORKSHEETS = {}


def get_ws(category):
    """Retourne une feuille existante selon la catégorie."""
    if category in WORKSHEETS:
        return WORKSHEETS[category]
    
    ws = sheet.worksheet(category)  # ATTENTION: la feuille doit déjà exister
    WORKSHEETS[category] = ws
    return ws


def write_to_sheet(category, urgence, synthese, email_date):
    """
    Écrit : ID | Date | Urgence | Synthèse
    dans l'onglet correspondant à la catégorie.
    """

    ws = get_ws(category)

    # Générer ID auto-incrémenté (nombre de lignes existantes)
    next_id = len(ws.col_values(1))  # compte la colonne A

    # Format de la date
    if not email_date:
        email_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        email_date = str(email_date)

    row = [
        next_id,
        email_date,
        urgence,
        synthese
    ]

    ws.append_row(row)
