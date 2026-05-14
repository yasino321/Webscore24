import os
import csv
import googlemaps
from dotenv import load_dotenv

load_dotenv()

def find_leads(branche: str, ort: str, radius_meter: int) -> list:
    """
    Nutzt Google Places API (Nearby Search)
    Gibt zurück: Name, Adresse, Website-URL, Telefonnummer, Google-Bewertungsanzahl
    Speichert Ergebnis in leads.csv
    """
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("Fehler: GOOGLE_PLACES_API_KEY nicht in .env gefunden.")
        return []

    gmaps = googlemaps.Client(key=api_key)

    # 1. Geocoding des Ortes
    geocode_result = gmaps.geocode(ort)
    if not geocode_result:
        print(f"Fehler: Ort '{ort}' konnte nicht gefunden werden.")
        return []

    location = geocode_result[0]['geometry']['location']

    # 2. Nearby Search
    # Note: nearby_search doesn't return website or phone number directly in the initial call
    # We might need place_details for each result
    places_result = gmaps.places_nearby(
        location=location,
        radius=radius_meter,
        keyword=branche
    )

    leads = []
    for place in places_result.get('results', []):
        place_id = place['place_id']

        # 3. Get Place Details
        details = gmaps.place(place_id=place_id, fields=['name', 'formatted_address', 'website', 'formatted_phone_number', 'rating', 'user_ratings_total'])
        result = details.get('result', {})

        lead = {
            'name': result.get('name'),
            'adresse': result.get('formatted_address'),
            'url': result.get('website'),
            'telefon': result.get('formatted_phone_number'),
            'bewertungen': result.get('user_ratings_total', 0),
            'status': 'neu',
            'score_gesamt': ''
        }

        if lead['url']: # Nur Leads mit Website machen Sinn für dieses Tool
            leads.append(lead)
            _save_to_csv(lead)

    return leads

def add_manual(url: str):
    """Funktion um einzelne URLs manuell hinzuzufügen"""
    lead = {
        'name': 'Manuell hinzugefügt',
        'adresse': 'N/A',
        'url': url,
        'telefon': 'N/A',
        'bewertungen': 0,
        'status': 'neu',
        'score_gesamt': ''
    }
    _save_to_csv(lead)
    print(f"Lead manuell hinzugefügt: {url}")

def _save_to_csv(lead: dict):
    file_exists = os.path.isfile('leads.csv')
    with open('leads.csv', mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'adresse', 'url', 'telefon', 'bewertungen', 'status', 'score_gesamt'])
        if not file_exists:
            writer.writeheader()
        writer.writerow(lead)

if __name__ == "__main__":
    # Test (wird fehlschlagen ohne API Key)
    # find_leads("Friseur", "Berlin Neukölln", 2000)
    pass
