# WebScore

WebScore ist ein leistungsstarkes lokales CLI-Tool für die Analyse von Websites lokaler Unternehmen. Es kombiniert Scraping, KI-basierte Bewertung, automatische Website-Generierung und die Erstellung von PDF-Verkaufsberichten in einem vollautomatischen Workflow.

## Ziel des Tools
Das Tool hilft dabei, potenzielle Kunden (Leads) mit verbesserungswürdigen Websites zu finden, diese objektiv zu bewerten und ihnen sofort ein konkretes Angebot inklusive eines modernen Website-Entwurfs zu präsentieren.

## Funktionen
- **Lead-Finder**: Automatische Suche nach Unternehmen über die Google Places API.
- **Website-Analyse**: Bewertung von Design, Call-to-Actions und Rechtssicherheit mittels KI.
- **Automatischer Entwurf**: Generierung einer modernen, responsiven Ersatz-Website (Single-File HTML).
- **Verkaufs-Reporting**: Erstellung eines professionellen 4-seitigen PDF-Reports mit Screenshot-Vergleich und Kostenvorschlag.

## Tech Stack
- **Sprache**: Python 3.11+
- **KI-Modelle**: Google Gemini (Analyse), OpenAI GPT-4o & Big Pickle (Generierung)
- **Scraping & Screenshots**: Requests, BeautifulSoup4 & Playwright (Headless Chromium)
- **PDF-Erstellung**: ReportLab
- **Datenhaltung**: Lokale `leads.csv`

## Installation

1.  **Repository klonen** (oder Dateien kopieren).
2.  **Abhängigkeiten installieren**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Playwright Browser installieren**:
    ```bash
    playwright install chromium
    ```
4.  **Konfiguration**: Erstelle eine `.env` Datei im Hauptverzeichnis mit folgendem Inhalt:
    ```env
    BIG_PICKLE_API_KEY=dein_opencode_zen_key
    OPENAI_API_KEY=dein_openai_key
    GEMINI_API_KEY=dein_gemini_key
    GOOGLE_PLACES_API_KEY=dein_google_key
    ```

## Benutzung

Das Tool wird über die `main.py` gesteuert:

### 1. Leads finden
Sucht nach Unternehmen in einer bestimmten Branche und an einem bestimmten Ort.
```bash
python main.py finden --branche "Friseur" --ort "Berlin Neukölln" --radius 2000
```

### 2. Leads manuell hinzufügen
Falls Sie bereits eine spezifische URL im Kopf haben:
```bash
python main.py hinzufügen --url "https://beispiel-website.de"
```

### 3. Analysieren
Analysiert alle in der `leads.csv` als "neu" markierten Einträge.
```bash
python main.py analysieren
```

### 4. Generieren (Einzelner Lead)
Führt die Analyse, Website-Generierung und Report-Erstellung für einen spezifischen Lead aus. Die Ergebnisse werden im Ordner `/output` gespeichert.
```bash
python main.py generieren --name "Musterfirma" --url "https://muster-firma.de" --branche "Friseur"
```

## Projektstruktur
- `main.py`: Zentrales CLI-Einstiegspunkt.
- `finder.py`: Logik für Google Places Suche.
- `analyser.py`: Screenshot-Erstellung und KI-Analyse.
- `generator.py`: Generierung der neuen HTML-Website.
- `reporter.py`: PDF-Erstellung.
- `leads.csv`: Lokale "Datenbank" für alle Leads.
- `output/`: Gespeicherte Screenshots, HTML-Entwürfe und PDF-Reports.

---
*Hinweis: Dieses Tool wurde unter Berücksichtigung moderner KI-Workflows entwickelt, wobei der Fokus auf Präzision und Geschwindigkeit liegt.*
