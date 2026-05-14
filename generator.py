import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate(url: str, branche: str) -> str:
    """
    Liest HTML der alten Website
    Schickt an OpenAI API (GPT-4o) mit Auftrag: Generiere eine vollständige, moderne, deutsche HTML/CSS-Website
    """
    print(f"Generiere neue Website für: {url} ({branche})")

    # 1. HTML laden
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        old_html = response.text
        soup = BeautifulSoup(old_html, 'html.parser')
        # Firmenname versuchen zu finden
        firmenname = soup.title.string if soup.title else "Unbekannt"
        # Säubern für Dateinamen
        firmenname_clean = "".join([c for c in firmenname if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
        if not firmenname_clean:
            firmenname_clean = "Firma"
    except Exception as e:
        print(f"Fehler beim Laden der alten Website für Generator: {e}")
        firmenname_clean = "Firma"
        old_html = "Keine Inhalte gefunden."

    # 2. Big Pickle API für Website-Generierung (OpenCode Zen)
    api_key = os.getenv("BIG_PICKLE_API_KEY")
    if not api_key:
        print("Fehler: BIG_PICKLE_API_KEY nicht in .env gefunden. Nutze OpenAI Fallback...")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Fehler: Kein API Key für Generierung gefunden.")
            return ""
        client = OpenAI(api_key=api_key)
        model_name = "gpt-4o"
    else:
        # Big Pickle (OpenCode Zen) nutzt OpenAI-kompatible API
        client = OpenAI(api_key=api_key, base_url="https://opencode.ai/zen/v1")
        model_name = "big-pickle"

    prompt = f"Lies den folgenden HTML-Inhalt der alten Website einer Firma aus der Branche {branche}:\n\n{old_html[:10000]}\n\nGeneriere eine vollständige, moderne, deutsche HTML/CSS-Website (single file, kein Framework, inline CSS) für ein Unternehmen der Branche {branche}. Übernehme vorhandene Inhalte (Firmenname, Leistungen, Kontakt). Die Seite soll: klares Header-Bild (nutze Platzhalter von Unsplash), deutliche CTA-Buttons, Leistungsübersicht, Kontaktbereich mit Telefon + Adresse, vollständiges Impressum-Platzhalter-Sektion enthalten. Antworte NUR mit dem HTML-Code, kein erklärender Text."

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Du bist ein erfahrener Webdesigner."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000
        )

        new_html = response.choices[0].message.content

        # Säubern falls OpenAI Markdown-Tags mitschickt
        if "```html" in new_html:
            new_html = new_html.split("```html")[1].split("```")[0].strip()
        elif "```" in new_html:
            new_html = new_html.split("```")[1].split("```")[0].strip()

        os.makedirs("output", exist_ok=True)
        output_path = f"output/{firmenname_clean}_neu.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_html)

        print(f"Neue Website gespeichert unter: {output_path}")
        return output_path

    except Exception as e:
        print(f"Fehler bei der Website-Generierung: {e}")
        return ""

if __name__ == "__main__":
    pass
