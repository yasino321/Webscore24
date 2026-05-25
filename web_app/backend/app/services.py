import os
import json
import requests
import tempfile
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import google.generativeai as genai
from openai import OpenAI
import PIL.Image
import googlemaps
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from datetime import datetime
from . import models

def find_leads_service(branche: str, ort: str, radius: int, user: models.User):
    api_key = user.google_places_api_key
    if not api_key:
        raise Exception("Google Places API Key missing in user settings.")

    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(ort)
    if not geocode_result:
        return []

    location = geocode_result[0]['geometry']['location']
    places_result = gmaps.places_nearby(
        location=location,
        radius=radius,
        keyword=branche
    )

    leads = []
    for place in places_result.get('results', []):
        place_id = place['place_id']
        details = gmaps.place(place_id=place_id, fields=['name', 'formatted_address', 'website', 'formatted_phone_number', 'user_ratings_total'])
        result = details.get('result', {})

        if result.get('website'):
            leads.append({
                'name': result.get('name'),
                'address': result.get('formatted_address'),
                'url': result.get('website'),
                'phone': result.get('formatted_phone_number'),
                'reviews_count': result.get('user_ratings_total', 0)
            })
    return leads

def analyse_service(url: str, user: models.User):
    api_key = user.gemini_api_key
    if not api_key:
        raise Exception("Gemini API Key missing in user settings.")

    # 1. Load HTML
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text()[:4000]

    # 2. Screenshot
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        screenshot_path = tmp.name

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 800})
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.screenshot(path=screenshot_path)
            browser.close()

        # 3. Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        system_prompt = "Du bist ein Website-Analyst. Bewerte die folgende Website nach drei Kriterien: 1) Design & Ästhetik (0-33 Punkte), 2) Call-to-Actions (0-33 Punkte), 3) Impressum & Pflichtangaben (0-34 Punkte). Antworte NUR als JSON: {\"design\": Zahl, \"cta\": Zahl, \"impressum\": Zahl, \"gesamt\": Zahl, \"begruendung\": \"String\"}"

        img = PIL.Image.open(screenshot_path)
        response = model.generate_content([f"HTML-Inhalt:\n\n{text_content}", system_prompt, img])

        result_text = response.text
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        return json.loads(result_text)
    finally:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

def generate_website_service(url: str, branche: str, user: models.User):
    api_key_oa = user.openai_api_key
    api_key_gm = user.gemini_api_key

    try:
        res = requests.get(url, timeout=5)
        old_content = res.text[:5000]
    except:
        old_content = "Keine Inhalte gefunden."

    prompt = f"Generiere eine moderne, deutsche HTML/CSS-Website (single file, inline CSS) für ein Unternehmen der Branche {branche} basierend auf diesen Inhalten: {old_content}. Antworte NUR mit dem HTML-Code."

    if api_key_oa:
        client = OpenAI(api_key=api_key_oa)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        html = response.choices[0].message.content
    elif api_key_gm:
        genai.configure(api_key=api_key_gm)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        html = response.text
    else:
        raise Exception("Kein API Key für Website-Generierung konfiguriert.")

    if "```html" in html:
        html = html.split("```html")[1].split("```")[0].strip()
    return html

def create_report_pdf(lead: models.Lead, analysis: dict, new_html: str, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1,
        spaceAfter=30
    )

    content = []
    content.append(Spacer(1, 100))
    content.append(Paragraph(f"Website-Analyse & Angebot", title_style))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"Für: {lead.name}", styles['Heading2']))
    content.append(Paragraph(f"Website: {lead.url}", styles['Normal']))
    content.append(Spacer(1, 50))
    content.append(Paragraph(f"Datum: {datetime.now().strftime('%d.%m.%Y')}", styles['Normal']))
    content.append(PageBreak())

    content.append(Paragraph("Analyse Ihrer aktuellen Website", styles['Heading1']))
    content.append(Spacer(1, 20))

    data = [
        ['Kriterium', 'Punkte'],
        ['Design & Ästhetik', f"{analysis.get('design', 0)} / 33"],
        ['Call-to-Actions', f"{analysis.get('cta', 0)} / 33"],
        ['Impressum & Pflichtangaben', f"{analysis.get('impressum', 0)} / 34"],
        ['Gesamtbewertung', f"{analysis.get('gesamt', 0)} / 100"]
    ]

    t = Table(data, colWidths=[300, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(t)
    content.append(Spacer(1, 20))
    content.append(Paragraph("Begründung:", styles['Heading3']))
    content.append(Paragraph(analysis.get('begruendung', ''), styles['Normal']))

    doc.build(content)
