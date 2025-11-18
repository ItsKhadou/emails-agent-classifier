from gmail_reader import get_email_data
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("📥 Lecture des emails Gmail en cours...\n")

emails = get_email_data(n=5)

for i, email in enumerate(emails, start=1):
    print(f"--- Email {i} ---")
    print("Sujet :", email["subject"])
    print("Corps :", email["body"][:150])
    print()
