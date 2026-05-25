import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Key, Save, CheckCircle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Settings = () => {
  const { user, token, fetchUser } = useAuth();
  const [keys, setKeys] = useState({
    gemini_api_key: user?.gemini_api_key || '',
    openai_api_key: user?.openai_api_key || '',
    google_places_api_key: user?.google_places_api_key || '',
  });
  const [saved, setSaved] = useState(false);

  const saveSettings = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/users/me/keys`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(keys)
      });
      if (res.ok) {
        await fetchUser();
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div className="max-w-2xl space-y-8 animate-in fade-in duration-500">
      <header>
        <h2 className="text-3xl font-bold">Einstellungen</h2>
        <p className="text-slate-400 mt-1">Verwalten Sie Ihre API-Schlüssel und Kontoeinstellungen</p>
      </header>

      <section className="bg-slate-900/50 border border-slate-800 p-8 rounded-2xl backdrop-blur-sm">
        <form onSubmit={saveSettings} className="space-y-6">
          <div className="flex items-center space-x-3 text-blue-500 mb-2">
            <Key size={20} />
            <h3 className="text-lg font-semibold text-slate-100">API Konfiguration</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Google Gemini API Key</label>
              <input
                type="password"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                value={keys.gemini_api_key}
                onChange={e => setKeys({...keys, gemini_api_key: e.target.value})}
                placeholder="••••••••••••••••"
              />
              <p className="text-[10px] text-slate-500 mt-1">Wird für die Website-Analyse und Free Mode Generierung benötigt.</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">OpenAI API Key (Premium)</label>
              <input
                type="password"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                value={keys.openai_api_key}
                onChange={e => setKeys({...keys, openai_api_key: e.target.value})}
                placeholder="••••••••••••••••"
              />
              <p className="text-[10px] text-slate-500 mt-1">Wird für hochwertige Website-Entwürfe (GPT-4o) genutzt.</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Google Places API Key</label>
              <input
                type="password"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                value={keys.google_places_api_key}
                onChange={e => setKeys({...keys, google_places_api_key: e.target.value})}
                placeholder="••••••••••••••••"
              />
              <p className="text-[10px] text-slate-500 mt-1">Erforderlich für die Lead-Suche.</p>
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition-all flex items-center justify-center space-x-2"
          >
            {saved ? <CheckCircle size={20} /> : <Save size={20} />}
            <span>{saved ? 'Gespeichert' : 'Einstellungen speichern'}</span>
          </button>
        </form>
      </section>
    </div>
  );
};

export default Settings;
