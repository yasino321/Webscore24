# WebScore Web - Dokumentation & Guide

Willkommen zur Web-Version von WebScore! Diese Version wurde entwickelt, um als pure Client-Side Applikation direkt im Browser (auch mobil) zu laufen und kann einfach über GitHub Pages gehostet werden.

## 🚀 Funktionen der Web-Version

- **Lead-Finder (Kostenlos & Premium)**: Suche nach Unternehmen in deiner Nähe. Der "Free Mode" nutzt OpenStreetMap, während der Premium-Modus die Google Places API anspricht.
- **Manueller Import**: Füge Leads direkt über eine URL hinzu.
- **KI-Analyse**: Nutzt Google Gemini 1.5 Flash, um Websites in Sekunden auf Design, Call-to-Actions und Rechtssicherheit zu prüfen.
- **Website-Generator**: Erstellt einen modernen HTML/CSS-Entwurf basierend auf der alten Website. Unterstützt GPT-4o und Gemini.
- **PDF-Reporting**: Erstellt einen professionellen Verkaufsbericht als PDF direkt im Browser zum Download.

## 🛠️ Anleitung für beste Ergebnisse

Um das Maximum aus WebScore herauszuholen und potenzielle Kunden mit überzeugenden Reports zu gewinnen, befolge diese Tipps:

### 1. API-Keys optimal nutzen
- **Gemini 1.5 Flash**: Dies ist das Herzstück für die Analyse. Es ist extrem schnell und kosteneffizient (oft kostenlos im Free Tier). Sorge dafür, dass dein Key in den Einstellungen hinterlegt ist.
- **GPT-4o (OpenAI)**: Für die Website-Generierung liefert GPT-4o oft die ästhetisch ansprechenderen Ergebnisse und besseren Code-Strukturen im Vergleich zu kleineren Modellen.

### 2. Lead-Suche verfeinern
- Nutze im **Free Mode** (OSM) präzise Begriffe für die Branche (z.B. "hairdresser" statt "Friseur"), da OpenStreetMap oft englische Tags verwendet.
- Im **Premium Modus** (Google) sind deutsche Begriffe kein Problem. Ein Radius von 2000-5000m liefert meist die relevantesten lokalen Ergebnisse.

### 3. Der Analyse-Prozess
- WebScore nutzt einen CORS-Proxy (`allorigins`), um Website-Inhalte zu lesen. Bei manchen sehr stark geschützten Websites kann das Scraping fehlschlagen. In diesem Fall wird der Lead als "fehler" markiert.
- **Qualifizierung**: Ein Lead gilt als "qualifiziert", wenn der Gesamtscore unter 60 Punkten liegt. Diese Unternehmen haben den größten Bedarf an einer neuen Website.

### 4. Den Report erstellen
- Bevor du den Report generierst, stelle sicher, dass du in den Einstellungen die entsprechenden Keys für die Generierung (OpenAI oder Gemini) aktiv hast.
- Der Report enthält einen Platzhalter für den Website-Screenshot (via WordPress mshots). Da dieser Dienst die Seite erst beim ersten Aufruf rendert, kann es beim ersten Mal einen Moment dauern, bis das Bild im PDF erscheint oder es wird ein Platzhalter angezeigt.

### 5. Hosting auf GitHub
Da dies eine statische Seite ist:
1. Lade den `web/` Ordner in dein GitHub Repository hoch.
2. Aktiviere **GitHub Pages** in den Repository-Einstellungen.
3. Wähle den `/web` Ordner als Quelle.
4. Fertig! Deine eigene Sales-Plattform ist weltweit erreichbar.

## 🔒 Sicherheitshinweis
Alle deine API-Keys und Lead-Daten werden **ausschließlich lokal in deinem Browser (localStorage)** gespeichert. Es findet keine Übertragung an unsere Server statt. Wenn du den Browser-Cache löschst, werden auch deine Einstellungen und Leads gelöscht – exportiere deine Leads daher regelmäßig als CSV!
