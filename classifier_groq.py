import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import requests

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY manquant dans .env")

# 🔥 BON MODELE pour Groq (nom exact)
MODEL = "openai/gpt-oss-20b"
TEMPERATURE = 0.0

PROMPT_TEMPLATE = (BASE_DIR / "prompt.txt").read_text(encoding="utf-8")

ALLOWED_CATEGORIES = {
    "Problème technique informatique",
    "Demande administrative",
    "Problème d’accès / authentification",
    "Demande de support utilisateur",
    "Bug ou dysfonctionnement d’un service",
}

ALLOWED_URGENCES = {
    "Critique",
    "Élevée",
    "Modérée",
    "Faible",
    "Anodine",
}

DEFAULT_RESULT = {
    "categorie": "Inconnu",
    "urgence": "Anodine",
    "synthese": "Impossible de générer une synthèse. Le modèle n'a pas renvoyé un JSON valide."
}


def _normalize_result(raw):
    if not isinstance(raw, dict):
        return DEFAULT_RESULT.copy()

    categorie = raw.get("categorie", "").strip()
    urgence = raw.get("urgence", "").strip()
    synthese = raw.get("synthese", "").strip()

    if categorie not in ALLOWED_CATEGORIES:
        categorie = "Inconnu"

    if urgence not in ALLOWED_URGENCES:
        urgence = "Anodine"

    if not synthese:
        synthese = DEFAULT_RESULT["synthese"]

    return {
        "categorie": categorie,
        "urgence": urgence,
        "synthese": synthese
    }


def _extract_json(text: str):
    if not text:
        return DEFAULT_RESULT.copy()

    text = text.strip()

    try:
        return _normalize_result(json.loads(text))
    except:
        pass

    cleaned = text.replace("```json", "").replace("```", "").strip()
    try:
        return _normalize_result(json.loads(cleaned))
    except:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        try:
            return _normalize_result(json.loads(text[start:end+1]))
        except:
            pass

    return DEFAULT_RESULT.copy()


def classify_ticket(subject: str, body: str) -> dict:
    """
    Classifie un ticket en appelant Groq — un mail à la fois.
    Gestion automatique des erreurs, rate-limit 429, et retries.
    """

    prompt = PROMPT_TEMPLATE.format(subject=subject, body=body)

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE
    }

    max_retries = 5

    for attempt in range(1, max_retries + 1):

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json=payload,
                timeout=60
            )

            # --- Gestion du rate limit 429 ---
            if response.status_code == 429:
                error_data = response.json()
                msg = error_data.get("error", {}).get("message", "")
                wait_seconds = 10

                if "try again in" in msg:
                    try:
                        wait_seconds = float(msg.split("try again in ")[1].split("s")[0])
                    except:
                        wait_seconds = 10

                print(f"[Groq] 🚧 Rate limit — pause {wait_seconds:.1f} sec")
                time.sleep(wait_seconds)
                continue

            # --- Autres erreurs HTTP ---
            if response.status_code != 200:
                print(f"[Groq] Erreur HTTP {response.status_code}: {response.text}")
                time.sleep(2 * attempt)
                continue

            data = response.json()

            if "error" in data:
                print(f"[Groq] Erreur API: {data['error']}")
                time.sleep(2 * attempt)
                continue

            content = data["choices"][0]["message"]["content"]
            return _extract_json(content)

        except Exception as e:
            print(f"[Groq] Exception: {e}")
            time.sleep(2 * attempt)

    # --- En cas d'échec total ---
    return DEFAULT_RESULT.copy()
