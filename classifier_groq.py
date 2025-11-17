import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import requests

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "openai/gpt-oss-20b"

PROMPT_TEMPLATE = (BASE_DIR / "prompt.txt").read_text(encoding="utf-8")


def classify_ticket(subject, body):

    prompt = PROMPT_TEMPLATE.format(subject=subject, body=body)

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    while True:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json=payload
        )

        data = response.json()
        print("RAW GROQ =", data)

        # ----- Gestion du rate_limit -----
        if "error" in data and data["error"].get("code") == "rate_limit_exceeded":
            print("⏳ Rate limit atteint, attente 5 secondes...")
            time.sleep(5)
            continue  # recommence la boucle

        # ----- Sortie validée -----
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]

            try:
                return json.loads(content)
            except:
                cleaned = content.strip().replace("```json", "").replace("```", "")
                return json.loads(cleaned)

        raise Exception("Invalid response: " + str(data))
