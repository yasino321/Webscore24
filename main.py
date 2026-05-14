import argparse
import csv
import os
import sys
from finder import find_leads, add_manual
from analyser import analyse
from generator import generate
from reporter import create_report

def main():
    parser = argparse.ArgumentParser(description="WebScore - Website Analyse & Sales Tool")
    subparsers = parser.add_subparsers(dest="command", help="Befehle")

    # Befehl: finden
    find_parser = subparsers.add_parser("finden", help="Neue Leads über Google Maps finden")
    find_parser.add_argument("--branche", required=True, help="Branche (z.B. Friseur)")
    find_parser.add_argument("--ort", required=True, help="Ort (z.B. Berlin Neukölln)")
    find_parser.add_argument("--radius", type=int, default=2000, help="Suchradius in Metern")

    # Befehl: hinzufügen
    add_parser = subparsers.add_parser("hinzufügen", help="Lead manuell über URL hinzufügen")
    add_parser.add_argument("--url", required=True, help="Website URL")

    # Befehl: analysieren
    analyse_parser = subparsers.add_parser("analysieren", help="Alle neuen Leads in leads.csv analysieren")

    # Befehl: generieren
    gen_parser = subparsers.add_parser("generieren", help="Website und Report für einen Lead erstellen")
    gen_parser.add_argument("--name", required=True, help="Firmenname")
    gen_parser.add_argument("--url", required=True, help="Website URL")
    gen_parser.add_argument("--branche", required=True, help="Branche")

    args = parser.parse_args()

    if args.command == "finden":
        print(f"Suche nach Leads in {args.ort} (Branche: {args.branche}, Radius: {args.radius}m)...")
        leads = find_leads(args.branche, args.ort, args.radius)
        print(f"{len(leads)} Leads gefunden und in leads.csv gespeichert.")

    elif args.command == "hinzufügen":
        add_manual(args.url)

    elif args.command == "analysieren":
        if not os.path.exists("leads.csv"):
            print("leads.csv nicht gefunden. Nutze 'finden' zuerst.")
            return

        leads_to_analyse = []
        with open("leads.csv", mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('status') == "neu":
                    leads_to_analyse.append(row)

        if not leads_to_analyse:
            print("Keine neuen Leads zum Analysieren gefunden.")
            return

        print(f"Analysiere {len(leads_to_analyse)} Leads...")
        for lead in leads_to_analyse:
            analyse(lead['url'])

        print("Analyse abgeschlossen.")

    elif args.command == "generieren":
        # 1. Analyse durchführen (falls noch nicht geschehen)
        score = analyse(args.url)
        if not score:
            print("Fehler bei der Analyse der Website.")
            return

        screenshot_alt = f"output/{args.url.replace('https://', '').replace('http://', '').replace('/', '_')}.png"

        # 2. Website generieren
        html_path = generate(args.url, args.branche)
        if not html_path:
            print("Fehler bei der Website-Generierung.")
            return

        # 3. Report erstellen
        pdf_path = create_report(args.name, args.branche, score, screenshot_alt, html_path)
        print(f"Report erfolgreich erstellt: {pdf_path}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
