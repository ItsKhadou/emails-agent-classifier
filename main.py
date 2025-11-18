import asyncio
from gmail_reader import get_email_data
from classifier_groq import classify_ticket
from sheets_writer import write_to_sheet


async def process_email(email):
    subject = email["subject"]
    body = email["body"]
    date = email["date"]

    print(f"\n📌 Mail : {subject}")

    # Classification Groq
    result = classify_ticket(subject, body)

    categorie = result["categorie"]
    urgence = result["urgence"]
    synthese = result["synthese"]

    print(f"➡️ Catégorie : {categorie}")
    print(f"➡️ Urgence   : {urgence}")

    # Écriture Google Sheet
    await asyncio.to_thread(
        write_to_sheet,
        categorie,
        urgence,
        synthese,
        date
    )

    print("✔️ Enregistré dans Google Sheets.")


async def main():
    print("📥 Lecture des emails Gmail...")
    emails = get_email_data(n=50)

    if not emails:
        print("❌ Aucun email trouvé.")
        return

    print(f"📨 {len(emails)} emails récupérés.")

    # Traitement séquentiel pour éviter Groq 429
    for email in emails:
        try:
            await process_email(email)
        except Exception as e:
            print(f"⚠️ Erreur : {e}")
            continue

    print("\n🎉 Traitement terminé !")


if __name__ == "__main__":
    asyncio.run(main())
