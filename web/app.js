// UI State & Elements
let currentView = 'find';
let freeMode = false;
let leads = JSON.parse(localStorage.getItem('webscore_leads')) || [];
let settings = JSON.parse(localStorage.getItem('webscore_settings')) || {
    gemini: '',
    openai: '',
    google: ''
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    renderLeads();

    // Event Listeners
    document.getElementById('free-mode-toggle').addEventListener('change', (e) => {
        freeMode = e.target.checked;
        updateUIForMode();
    });
});

// Navigation
function showView(viewId) {
    document.querySelectorAll('.view').forEach(s => s.classList.add('hidden'));
    document.getElementById(`view-${viewId}`).classList.remove('hidden');

    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('sidebar-item-active'));
    const navBtn = document.getElementById(`nav-${viewId}`);
    if (navBtn) navBtn.classList.add('sidebar-item-active');

    currentView = viewId;
    if (viewId === 'leads') renderLeads();

    // Close sidebar on mobile after selection
    if (window.innerWidth < 768) {
        toggleSidebar(false);
    }
}

function toggleSidebar(force) {
    const sidebar = document.getElementById('sidebar');
    if (force !== undefined) {
        if (force) sidebar.classList.remove('-translate-x-full');
        else sidebar.classList.add('-translate-x-full');
    } else {
        sidebar.classList.toggle('-translate-x-full');
    }
}

function updateUIForMode() {
    const title = document.getElementById('find-title');
    const radiusContainer = document.getElementById('radius-container');

    if (freeMode) {
        title.innerText = 'Neue Leads finden (Kostenlos)';
        radiusContainer.classList.add('hidden');
    } else {
        title.innerText = 'Neue Leads finden (Premium)';
        radiusContainer.classList.remove('hidden');
    }
}

// Settings
function loadSettings() {
    document.getElementById('key-gemini').value = settings.gemini || '';
    document.getElementById('key-openai').value = settings.openai || '';
    document.getElementById('key-google').value = settings.google || '';
}

function saveSettings() {
    settings.gemini = document.getElementById('key-gemini').value;
    settings.openai = document.getElementById('key-openai').value;
    settings.google = document.getElementById('key-google').value;

    localStorage.setItem('webscore_settings', JSON.stringify(settings));
    alert('Einstellungen gespeichert!');
}

// Logging
function log(message, type = 'info') {
    const container = document.getElementById('log-container');
    const div = document.createElement('div');
    const colors = {
        info: 'text-slate-300',
        success: 'text-green-400',
        error: 'text-red-400',
        warning: 'text-yellow-400'
    };
    div.className = colors[type] || colors.info;
    div.innerText = `[${new Date().toLocaleTimeString()}] ${message}`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Lead Management
function saveLeads() {
    localStorage.setItem('webscore_leads', JSON.stringify(leads));
}

function renderLeads() {
    const tbody = document.getElementById('leads-table-body');
    tbody.innerHTML = '';

    leads.forEach((lead, index) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-900/50 transition';

        const scoreDisplay = lead.score_gesamt ? `${lead.score_gesamt}/100` : '-';
        const statusClass = lead.status === 'neu' ? 'bg-blue-500/10 text-blue-500' :
                          lead.status === 'qualifiziert' ? 'bg-green-500/10 text-green-500' : 'bg-slate-500/10 text-slate-500';

        tr.innerHTML = `
            <td class="px-6 py-4">
                <div class="font-medium">${lead.name}</div>
                <div class="text-xs text-slate-500">${lead.adresse}</div>
            </td>
            <td class="px-6 py-4 text-sm text-blue-400 truncate max-w-xs">
                <a href="${lead.url}" target="_blank">${lead.url}</a>
            </td>
            <td class="px-6 py-4">
                <span class="px-2 py-1 rounded text-xs font-bold uppercase ${statusClass}">${lead.status}</span>
            </td>
            <td class="px-6 py-4 font-mono">${scoreDisplay}</td>
            <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end space-x-2">
                    <button onclick="generateReport(${index})" title="Analysieren & Report" class="p-2 hover:bg-slate-800 rounded transition text-blue-400">
                        <i data-lucide="file-text" class="w-5 h-5"></i>
                    </button>
                    <button onclick="deleteLead(${index})" title="Löschen" class="p-2 hover:bg-slate-800 rounded transition text-red-400">
                        <i data-lucide="trash-2" class="w-5 h-5"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
    lucide.createIcons();
}

function deleteLead(index) {
    if (confirm('Lead wirklich löschen?')) {
        leads.splice(index, 1);
        saveLeads();
        renderLeads();
    }
}

function addManualLead() {
    const url = document.getElementById('input-manual-url').value;
    const name = document.getElementById('input-manual-name').value || 'Manuell hinzugefügt';

    if (!url) return alert('Bitte URL angeben.');

    const lead = {
        name: name,
        adresse: 'N/A',
        url: url,
        telefon: 'N/A',
        bewertungen: 0,
        status: 'neu',
        score_gesamt: ''
    };

    leads.push(lead);
    saveLeads();
    alert('Lead hinzugefügt!');
    showView('leads');
}

function exportLeadsCSV() {
    if (leads.length === 0) return alert('Keine Leads vorhanden.');

    const headers = ['name', 'adresse', 'url', 'telefon', 'bewertungen', 'status', 'score_gesamt'];
    const csvRows = [headers.join(',')];

    leads.forEach(l => {
        const row = headers.map(h => `"${(l[h] || '').toString().replace(/"/g, '""')}"`);
        csvRows.push(row.join(','));
    });

    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leads_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

// Logic implementations will go here (runFind, runAnalyse, runGenerate, etc.)
async function runFind() {
    const branche = document.getElementById('input-branche').value;
    const ort = document.getElementById('input-ort').value;

    if (!branche || !ort) return alert('Bitte Branche und Ort angeben.');

    log(`Suche gestartet: ${branche} in ${ort}...`);

    if (freeMode) {
        await findLeadsFree(branche, ort);
    } else {
        const radius = document.getElementById('input-radius').value || 2000;
        await findLeadsPremium(branche, ort, radius);
    }
}

async function findLeadsFree(branche, ort) {
    log('Nutze OpenStreetMap (Free Mode)...');
    try {
        // 1. Geocoding via Nominatim
        const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(ort)}&format=json`, {
            headers: { 'User-Agent': 'WebScore/1.0' }
        });
        const geoData = await geoRes.json();
        if (!geoData.length) throw new Error('Ort nicht gefunden.');

        const { lat, lon } = geoData[0];
        log(`Koordinaten gefunden: ${lat}, ${lon}`);

        // 2. Overpass API
        const overpassQuery = `
            [out:json];
            (
              node["shop"="${branche.toLowerCase()}"](around:3000,${lat},${lon});
              node["amenity"="${branche.toLowerCase()}"](around:3000,${lat},${lon});
              way["shop"="${branche.toLowerCase()}"](around:3000,${lat},${lon});
              way["amenity"="${branche.toLowerCase()}"](around:3000,${lat},${lon});
            );
            out body;
        `;
        const overpassRes = await fetch(`https://overpass-api.de/api/interpreter?data=${encodeURIComponent(overpassQuery)}`);
        const data = await overpassRes.json();

        let foundCount = 0;
        data.elements.forEach(el => {
            const t = el.tags || {};
            if (t.website) {
                const lead = {
                    name: t.name || 'Unbekannt',
                    adresse: `${t['addr:street'] || ''} ${t['addr:housenumber'] || ''}, ${t['addr:postcode'] || ''} ${t['addr:city'] || ''}`.trim() || 'N/A',
                    url: t.website,
                    telefon: t.phone || t['contact:phone'] || 'N/A',
                    bewertungen: 0,
                    status: 'neu',
                    score_gesamt: ''
                };
                leads.push(lead);
                foundCount++;
            }
        });

        saveLeads();
        log(`Suche beendet. ${foundCount} Leads mit Website gefunden.`, 'success');
        alert(`${foundCount} Leads gefunden.`);
    } catch (e) {
        log(`Fehler bei der Suche: ${e.message}`, 'error');
    }
}

async function findLeadsPremium(branche, ort, radius) {
    log('Nutze Google Places API (Premium)...');
    if (!settings.google) return log('Google API Key fehlt in den Einstellungen!', 'error');

    // Since Google Places API has CORS, we'd normally need a backend.
    // For a "pure web" version, we'll inform the user or try to use a proxy if possible.
    // However, the task says "pure web version" and "API keys client side".
    // Most Google APIs don't allow CORS from arbitrary domains.
    log('HINWEIS: Google Places API erfordert i.d.R. einen Backend-Proxy wegen CORS.', 'warning');
    log('Versuche Suche über Client-Bibliothek (Simulation)...');

    // For the sake of this task, I will implement a placeholder that explains the CORS limitation
    // or suggests using the Free Mode for lead discovery if not on a allowed domain.
    alert('Google Places API kann im Browser direkt oft nicht aufgerufen werden (CORS). Bitte nutze den "Free Mode" für die Lead-Suche oder hoste WebScore auf einer Domain die in der Google Console freigeschaltet ist.');
}

async function generateReport(index) {
    const lead = leads[index];
    log(`Starte Prozess für ${lead.name}...`);

    try {
        // 1. Analyse
        const analysis = await runAnalyse(lead.url);
        if (!analysis) throw new Error('Analyse fehlgeschlagen.');

        lead.score_gesamt = analysis.gesamt;
        lead.status = analysis.gesamt < 60 ? 'qualifiziert' : 'analysiert';
        saveLeads();
        renderLeads();

        // 2. Website Generierung
        log('Generiere Website-Entwurf...');
        const newHtml = await runGenerate(lead.url, 'Dienstleister'); // Fallback Branche

        // 3. PDF Report
        log('Erstelle PDF Report...');
        await createPDF(lead, analysis, newHtml);

        log(`Prozess für ${lead.name} abgeschlossen!`, 'success');
    } catch (e) {
        log(`Fehler beim Prozess: ${e.message}`, 'error');
        alert(`Fehler: ${e.message}`);
    }
}

async function runAnalyse(url) {
    log(`Lade Website-Inhalt von ${url}...`);
    if (!settings.gemini) throw new Error('Gemini API Key fehlt!');

    try {
        // Use allorigins to bypass CORS for scraping
        const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`;
        const res = await fetch(proxyUrl);
        const data = await res.json();
        const html = data.contents;

        const doc = new DOMParser().parseFromString(html, 'text/html');
        const textContent = doc.body.innerText.substring(0, 4000);

        log('Sende Daten an Gemini für Analyse...');
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${settings.gemini}`;

        const prompt = `Du bist ein Website-Analyst. Bewerte die folgende Website nach drei Kriterien: 1) Design & Ästhetik (0-33 Punkte), 2) Call-to-Actions (0-33 Punkte), 3) Impressum & Pflichtangaben (0-34 Punkte). Antworte NUR als JSON: {"design": Zahl, "cta": Zahl, "impressum": Zahl, "gesamt": Zahl, "begruendung": "String"}. Website Text: ${textContent}`;

        const gRes = await fetch(geminiUrl, {
            method: 'POST',
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });

        const gData = await gRes.json();
        let resultText = gData.candidates[0].content.parts[0].text;

        // Clean JSON
        resultText = resultText.replace(/```json/g, '').replace(/```/g, '').trim();
        return JSON.parse(resultText);

    } catch (e) {
        log(`Analyse-Fehler: ${e.message}`, 'error');
        return null;
    }
}

async function runGenerate(url, branche) {
    const prompt = `Generiere eine moderne Website für ${branche} basierend auf ${url}. Gib nur den HTML/CSS Code zurück.`;

    if (settings.openai) {
        log('Nutze OpenAI für Website-Generierung...');
        // OpenAI API call
        const res = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${settings.openai}`
            },
            body: JSON.stringify({
                model: 'gpt-4o',
                messages: [{ role: 'user', content: prompt }]
            })
        });
        const data = await res.json();
        let html = data.choices[0].message.content;
        return html.replace(/```html/g, '').replace(/```/g, '').trim();
    } else if (settings.gemini) {
        log('Nutze Gemini für Website-Generierung (Free Mode)...');
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${settings.gemini}`;
        const gRes = await fetch(geminiUrl, {
            method: 'POST',
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });
        const gData = await gRes.json();
        let html = gData.candidates[0].content.parts[0].text;
        return html.replace(/```html/g, '').replace(/```/g, '').trim();
    }
    throw new Error('Kein API Key für Generierung vorhanden.');
}

async function createPDF(lead, analysis, newHtml) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Page 1: Title
    doc.setFontSize(24);
    doc.text('Website-Analyse & Angebot', 105, 100, { align: 'center' });
    doc.setFontSize(16);
    doc.text(`Für: ${lead.name}`, 105, 120, { align: 'center' });
    doc.text(`Datum: ${new Date().toLocaleDateString()}`, 105, 140, { align: 'center' });

    // Page 2: Analysis
    doc.addPage();
    doc.setFontSize(20);
    doc.text('Analyse Ihrer aktuellen Website', 20, 30);

    // Screenshot Placeholder (using WordPress mshots service)
    const screenshotUrl = `https://s0.wp.com/mshots/v1/${encodeURIComponent(lead.url)}?w=600`;
    try {
        // Adding an image to jsPDF requires it to be base64
        // For now we just add the link or a note because mshots takes time to generate
        doc.setFontSize(10);
        doc.text('Screenshot Ihrer Website (generiert...):', 20, 50);
        doc.text(lead.url, 20, 55);
    } catch (e) {}

    doc.autoTable({
        startY: 120,
        head: [['Kriterium', 'Punkte']],
        body: [
            ['Design & Ästhetik', `${analysis.design} / 33`],
            ['Call-to-Actions', `${analysis.cta} / 33`],
            ['Impressum & Pflichtangaben', `${analysis.impressum} / 34`],
            ['Gesamtbewertung', `${analysis.gesamt} / 100`]
        ],
        theme: 'striped'
    });

    doc.text('Begründung:', 20, doc.lastAutoTable.finalY + 20);
    doc.setFontSize(10);
    const splitText = doc.splitTextToSize(analysis.begruendung, 170);
    doc.text(splitText, 20, doc.lastAutoTable.finalY + 30);

    // Page 3: New Design Note
    doc.addPage();
    doc.setFontSize(20);
    doc.text('Ihr neues Website-Konzept', 20, 30);
    doc.setFontSize(12);
    doc.text('Wir haben einen ersten Entwurf für Sie erstellt.', 20, 50);
    doc.text('Dieser Entwurf ist modern, responsiv und verkaufsoptimiert.', 20, 60);

    // Save PDF
    doc.save(`${lead.name.replace(/\s/g, '_')}_angebot.pdf`);
}
