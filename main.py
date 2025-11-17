from gmail_reader import get_email_data
from classifier_groq import classify_ticket
from sheets_writer import write_to_sheet
import time

print("📥 Lecture des emails Gmail en cours...")
emails = get_email_data(n=5)

for mail in emails:
    subject = mail["subject"]
    body = mail["body"]

    print(f"\n📌 Classification : {subject}")
    result = classify_ticket(subject, body)

    write_to_sheet(
        result["categorie"],
        subject,
        result["urgence"],
        result["synthese"]
    )

    print("✔️ Écrit dans Google Sheet !")
    time.sleep(1)
