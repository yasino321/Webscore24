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

## Installations-Anleitung (Windows)

Folgen Sie diesen Schritten, um WebScore auf einem Windows-System zu installieren:

1.  **Python installieren**:
    - Laden Sie Python 3.11 oder neuer von [python.org](https://www.python.org/downloads/) herunter.
    - **WICHTIG**: Aktivieren Sie bei der Installation die Checkbox **"Add Python to PATH"**.

2.  **Projekt kopieren**:
    - Laden Sie den Projektordner herunter und entpacken Sie ihn.

3.  **Terminal öffnen**:
    - Drücken Sie `Win + R`, geben Sie `cmd` ein und drücken Sie Enter.
    - Navigieren Sie mit `cd` in den Projektordner (z.B. `cd C:\Users\Name\Desktop\webscore`).

4.  **Virtuelle Umgebung erstellen (Empfohlen)**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

5.  **Abhängigkeiten installieren**:
    ```bash
    pip install -r requirements.txt
    ```

6.  **Playwright & Browser-Treiber installieren**:
    ```bash
    playwright install chromium
    ```

7.  **Konfiguration**:
    - Erstellen Sie im Hauptverzeichnis eine Datei namens `.env`.
    - Öffnen Sie diese mit einem Texteditor (z.B. Notepad) und fügen Sie Ihre API-Keys ein:
    ```env
    BIG_PICKLE_API_KEY=dein_opencode_zen_key
    OPENAI_API_KEY=dein_openai_key
    GEMINI_API_KEY=dein_gemini_key
    GOOGLE_PLACES_API_KEY=dein_google_key
    ```

## Benutzung

Das Tool kann sowohl über die grafische Oberfläche (GUI) als auch über die Kommandozeile (CLI) gesteuert werden.

### Grafische Oberfläche (GUI)
Um die moderne Benutzeroberfläche zu starten, führen Sie folgendes aus:
```bash
python gui.py
```
Dort können Sie bequem in Tabs Leads suchen, die Liste verwalten und Reports generieren. In den Einstellungen können Sie zudem Ihre API-Keys direkt eingeben.

### Kommandozeile (CLI)
Das Tool wird über `python main.py` mit verschiedenen Befehlen gesteuert:

## CLI-Befehlsreferenz

### 1. `finden`
Sucht neue Leads über Google Maps.
- `--branche`: (Pflicht) Die Branche des Unternehmens (z.B. "Zahnarzt").
- `--ort`: (Pflicht) Stadt oder Stadtteil (z.B. "Hamburg Altona").
- `--radius`: (Optional) Suchradius in Metern (Default: 2000).
- **Beispiel**: `python main.py finden --branche "Friseur" --ort "Berlin" --radius 5000`

### 2. `hinzufügen`
Fügt eine einzelne Website-URL manuell zur Liste hinzu.
- `--url`: (Pflicht) Die vollständige URL (z.B. "https://meine-seite.de").
- **Beispiel**: `python main.py hinzufügen --url "https://beispiel.de"`

### 3. `analysieren`
Analysiert alle Leads in der `leads.csv`, die den Status "neu" haben.
- Keine weiteren Argumente nötig.
- **Beispiel**: `python main.py analysieren`

### 4. `generieren`
Führt den kompletten Prozess (Analyse, Website-Bau, PDF-Report) für einen spezifischen Lead aus.
- `--name`: (Pflicht) Name des Unternehmens für den Report.
- `--url`: (Pflicht) Die Website des Unternehmens.
- `--branche`: (Pflicht) Branche für die Preisberechnung im Report.
- **Beispiel**: `python main.py generieren --name "Haarstudio Meyer" --url "https://meyer-haare.de" --branche "Friseur"`

## Projektstruktur
- `main.py`: Zentraler Einstiegspunkt.
- `finder.py`: Google Places API Integration.
- `analyser.py`: Website-Scraping & KI-Bewertung (Gemini).
- `generator.py`: KI-Website-Erstellung (Big Pickle/OpenAI).
- `reporter.py`: PDF-Report Generierung (ReportLab).
- `leads.csv`: Lokale Speicherung der Leads.
- `output/`: Alle generierten PDFs, HTMLs und Screenshots.

## Erstellung von Binärdateien (.exe / Linux Binary)

Um WebScore als eigenständige Applikation zu kompilieren, nutzen wir `PyInstaller`.

### Für Windows (.exe)
Führen Sie diesen Befehl in der PowerShell oder CMD aus:
```bash
pyinstaller --noconsole --onefile --add-data "venv/Lib/site-packages/customtkinter;customtkinter" gui.py
```
*(Hinweis: Pfad zu customtkinter ggf. anpassen)*

### Für Linux
```bash
pyinstaller --noconsole --onefile gui.py
```

Die fertige Datei finden Sie anschließend im Ordner `dist/`.

---
*Hinweis: Dieses Tool wurde für maximale Automatisierung entwickelt. Stellen Sie sicher, dass Ihr Internetzugang stabil ist und die API-Keys gültig sind.*
