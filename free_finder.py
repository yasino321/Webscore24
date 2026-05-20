import os
import csv
import requests

def find_leads_free(branche: str, ort: str) -> list:
    """
    Nutzt OpenStreetMap (Overpass API) um kostenlos Leads zu finden.
    """
    print(f"Kostenlose Suche (OSM) für {branche} in {ort}...")

    # 1. Koordinaten für den Ort finden via Nominatim
    geo_url = f"https://nominatim.openstreetmap.org/search?q={ort}&format=json"
    headers = {'User-Agent': 'WebScore/1.0'}
    try:
        geo_res = requests.get(geo_url, headers=headers).json()
        if not geo_res:
            print("Ort nicht gefunden.")
            return []
        lat = geo_res[0]['lat']
        lon = geo_res[0]['lon']
    except Exception as e:
        print(f"Fehler bei Geokodierung: {e}")
        return []

    # 2. Overpass API Query
    # Suche im Umkreis von 3000m
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["shop"="{branche.lower()}"](around:3000,{lat},{lon});
      node["amenity"="{branche.lower()}"](around:3000,{lat},{lon});
      way["shop"="{branche.lower()}"](around:3000,{lat},{lon});
      way["amenity"="{branche.lower()}"](around:3000,{lat},{lon});
    );
    out body;
    """

    leads = []
    try:
        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers)
        data = response.json()

        for element in data.get('elements', []):
            tags = element.get('tags', {})
            name = tags.get('name', 'Unbekannt')
            website = tags.get('website')
            phone = tags.get('phone') or tags.get('contact:phone', 'N/A')
            addr = f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}, {tags.get('addr:postcode', '')} {tags.get('addr:city', '')}"

            if website: # Nur Leads mit Website sind relevant
                lead = {
                    'name': name,
                    'adresse': addr.strip() or "N/A",
                    'url': website,
                    'telefon': phone,
                    'bewertungen': 0, # OSM hat keine Bewertungen
                    'status': 'neu',
                    'score_gesamt': ''
                }
                leads.append(lead)
                _save_to_csv(lead)

        return leads
    except Exception as e:
        print(f"Fehler bei OSM Suche: {e}")
        return []

def _save_to_csv(lead: dict):
    file_exists = os.path.isfile('leads.csv')
    with open('leads.csv', mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'adresse', 'url', 'telefon', 'bewertungen', 'status', 'score_gesamt'])
        if not file_exists:
            writer.writeheader()
        writer.writerow(lead)
