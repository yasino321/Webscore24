import os
import requests
from bs4 import BeautifulSoup
import anthropic
from dotenv import load_dotenv

load_dotenv()

def generate(url: str, branche: str) -> str:
    """
    Liest HTML der alten Website
    Schickt an Claude API mit Auftrag: Generiere eine vollständige, moderne, deutsche HTML/CSS-Website
    Speichert generierte Website als output/{firmenname}_neu.html
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

    # 2. Claude API für Website-Generierung
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Fehler: ANTHROPIC_API_KEY nicht in .env gefunden.")
        return ""

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"Lies den folgenden HTML-Inhalt der alten Website einer Firma aus der Branche {branche}:\n\n{old_html[:10000]}\n\nGeneriere eine vollständige, moderne, deutsche HTML/CSS-Website (single file, kein Framework, inline CSS) für ein Unternehmen der Branche {branche}. Übernehme vorhandene Inhalte (Firmenname, Leistungen, Kontakt). Die Seite soll: klares Header-Bild (nutze Platzhalter von Unsplash), deutliche CTA-Buttons, Leistungsübersicht, Kontaktbereich mit Telefon + Adresse, vollständiges Impressum-Platzhalter-Sektion enthalten. Antworte NUR mit dem HTML-Code, kein erklärender Text."

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        new_html = response.content[0].text

        # Säubern falls Claude Markdown-Tags mitschickt
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
