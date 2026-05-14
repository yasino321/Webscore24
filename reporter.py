import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from playwright.sync_api import sync_playwright

def create_report(firmenname: str, branche: str, score: dict, screenshot_alt_path: str, neue_website_path: str) -> str:
    """
    Erstellt PDF mit reportlab, DIN A4, auf Deutsch
    """
    os.makedirs("output", exist_ok=True)
    output_pdf_path = f"output/{firmenname.replace(' ', '_')}_angebot.pdf"
    doc = SimpleDocTemplate(output_pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1, # Center
        spaceAfter=30
    )

    content = []

    # --- Seite 1: Deckblatt ---
    content.append(Spacer(1, 100))
    content.append(Paragraph(f"Website-Analyse & Angebot", title_style))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"Für: {firmenname}", styles['Heading2']))
    content.append(Paragraph(f"Branche: {branche}", styles['Normal']))
    content.append(Spacer(1, 50))
    content.append(Paragraph(f"Datum: {datetime.now().strftime('%d.%m.%Y')}", styles['Normal']))
    content.append(PageBreak())

    # --- Seite 2: Analyse der alten Website ---
    content.append(Paragraph("Analyse Ihrer aktuellen Website", styles['Heading1']))
    content.append(Spacer(1, 20))

    if screenshot_alt_path and os.path.exists(screenshot_alt_path):
        img = Image(screenshot_alt_path, width=450, height=280)
        content.append(img)
        content.append(Spacer(1, 20))

    # Score Tabelle
    data = [
        ['Kriterium', 'Punkte'],
        ['Design & Ästhetik', f"{score.get('design', 0)} / 33"],
        ['Call-to-Actions', f"{score.get('cta', 0)} / 33"],
        ['Impressum & Pflichtangaben', f"{score.get('impressum', 0)} / 34"],
        ['Gesamtbewertung', f"{score.get('gesamt', 0)} / 100"]
    ]

    t = Table(data, colWidths=[300, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(t)
    content.append(Spacer(1, 20))

    content.append(Paragraph("Begründung:", styles['Heading3']))
    content.append(Paragraph(score.get('begruendung', 'Keine Begründung verfügbar.'), styles['Normal']))
    content.append(PageBreak())

    # --- Seite 3: Vorschau der neuen Website ---
    content.append(Paragraph("Vorschau Ihrer neuen Website", styles['Heading1']))
    content.append(Spacer(1, 10))
    content.append(Paragraph("So könnte Ihre neue Website aussehen:", styles['Normal']))
    content.append(Spacer(1, 20))

    # Screenshot der neuen HTML Datei
    screenshot_neu_path = neue_website_path.replace(".html", ".png")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1280, 'height': 800})
            # absolute path for playwright
            abs_path = "file://" + os.path.abspath(neue_website_path)
            page.goto(abs_path)
            page.screenshot(path=screenshot_neu_path)
            browser.close()

        if os.path.exists(screenshot_neu_path):
            img_neu = Image(screenshot_neu_path, width=450, height=280)
            content.append(img_neu)
    except Exception as e:
        content.append(Paragraph(f"Vorschau konnte nicht generiert werden: {e}", styles['Normal']))

    content.append(Spacer(1, 20))
    content.append(Paragraph("Vorteile der neuen Website:", styles['Heading3']))
    content.append(Paragraph("- Modernes, ansprechendes Design", styles['Normal']))
    content.append(Paragraph("- Optimiert für mobile Endgeräte", styles['Normal']))
    content.append(Paragraph("- Klare Handlungsaufforderungen für mehr Kundenanfragen", styles['Normal']))
    content.append(Paragraph("- Rechtssicher durch vollständiges Impressum", styles['Normal']))
    content.append(PageBreak())

    # --- Seite 4: Kostenvorschlag ---
    content.append(Paragraph("Unser Angebot für Sie", styles['Heading1']))
    content.append(Spacer(1, 20))

    preise = {
        "Friseur": "299€",
        "Kosmetik": "299€",
        "Restaurant": "299€",
        "Café": "299€",
        "Handwerker": "399€",
        "Einzelhandel": "349€",
        "B2B": "499€",
        "Dienstleister": "499€",
        "Sonstige": "349€"
    }

    preis = preise.get(branche, preise["Sonstige"])
    # Fallback if branche contains one of the keys
    for k, v in preise.items():
        if k.lower() in branche.lower():
            preis = v
            break

    content.append(Paragraph(f"Festpreis für Ihre neue Website: {preis}", styles['Heading2']))
    content.append(Spacer(1, 20))

    content.append(Paragraph("Leistungsumfang:", styles['Heading3']))
    items = [
        "• Erstellung des individuellen Webdesigns",
        "• Übernahme Ihrer Texte und Bilder",
        "• Einbau von Kontaktmöglichkeiten (Telefon, Email)",
        "• Rechtssicheres Grundgerüst für Impressum & Datenschutz",
        "• Lieferung aller Dateien zur freien Verwendung",
        "• Kostenfreie Installation auf Ihrer vorhandenen Hardware / Webspace"
    ]
    for item in items:
        content.append(Paragraph(item, styles['Normal']))

    content.append(Spacer(1, 50))
    content.append(Paragraph("Interesse? Kontaktieren Sie uns für den nächsten Schritt!", styles['Heading3']))

    # Build PDF
    doc.build(content)

    return output_pdf_path

if __name__ == "__main__":
    pass
