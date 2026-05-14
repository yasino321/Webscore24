import os
import csv
import base64
import json
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import anthropic
from dotenv import load_dotenv

load_dotenv()

def analyse(url: str) -> dict:
    """
    Lädt HTML der URL mit requests/BeautifulSoup
    Macht Screenshot mit playwright (1280x800px, speichert als PNG)
    Schickt HTML-Text + Screenshot (base64) an Claude API
    """
    print(f"Analysiere: {url}")

    # 1. HTML laden
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        # Kürzen des HTML für die API, um Token zu sparen (nur Body-Text und Struktur)
        text_content = soup.get_text()[:4000]
    except Exception as e:
        print(f"Fehler beim Laden von {url}: {e}")
        _update_lead_status(url, "fehler")
        return None

    # 2. Screenshot machen
    os.makedirs("output", exist_ok=True)
    screenshot_path = f"output/{url.replace('https://', '').replace('http://', '').replace('/', '_')}.png"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 800})
            page.goto(url, wait_until="networkidle")
            page.screenshot(path=screenshot_path)
            browser.close()
    except Exception as e:
        print(f"Fehler beim Screenshot von {url}: {e}")
        screenshot_path = None

    # 3. Claude API Analyse
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Fehler: ANTHROPIC_API_KEY nicht in .env gefunden.")
        return None

    client = anthropic.Anthropic(api_key=api_key)

    base64_image = ""
    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    system_prompt = "Du bist ein Website-Analyst. Bewerte die folgende Website nach drei Kriterien: 1) Design & Ästhetik (0-33 Punkte): Ist die Seite modern, übersichtlich, professionell? 2) Call-to-Actions (0-33 Punkte): Gibt es klare Handlungsaufforderungen wie Telefonnummer, Kontaktformular, Terminbuchung? 3) Impressum & Pflichtangaben (0-34 Punkte): Sind Impressum, Datenschutzerklärung und Kontaktdaten vollständig vorhanden? Antworte NUR als JSON: {design: Zahl, cta: Zahl, impressum: Zahl, gesamt: Zahl, begruendung: String}"

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Hier ist der HTML-Text der Website:\n\n{text_content}"
                }
            ]
        }
    ]

    if base64_image:
        messages[0]["content"].append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_image
            }
        })

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620", # Claude 3.5 Sonnet is current state of the art
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )

        # Claude returns a message object, content is a list of blocks
        content_text = response.content[0].text
        # JSON parsen
        try:
            # Clean possible markdown block
            if "```json" in content_text:
                content_text = content_text.split("```json")[1].split("```")[0].strip()
            elif "```" in content_text:
                content_text = content_text.split("```")[1].split("```")[0].strip()

            analysis_result = json.loads(content_text)

            # Score in leads.csv schreiben
            _update_lead_score(url, analysis_result['gesamt'], analysis_result)

            return analysis_result
        except Exception as e:
            print(f"Fehler beim Parsen der Claude-Antwort: {e}")
            print(f"Antwort war: {content_text}")
            return None

    except Exception as e:
        print(f"Fehler bei der Claude API: {e}")
        return None

def _update_lead_status(url: str, status: str):
    rows = []
    updated = False
    if not os.path.exists('leads.csv'):
        return
    with open('leads.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['url'] == url:
                row['status'] = status
                updated = True
            rows.append(row)

    if updated:
        with open('leads.csv', mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

def _update_lead_score(url: str, score: int, analysis_dict: dict):
    rows = []
    updated = False
    if not os.path.exists('leads.csv'):
        return
    with open('leads.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['url'] == url:
                row['score_gesamt'] = score
                if score < 60:
                    row['status'] = "qualifiziert"
                else:
                    row['status'] = "analysiert"
                updated = True
            rows.append(row)

    if updated:
        with open('leads.csv', mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

if __name__ == "__main__":
    pass
