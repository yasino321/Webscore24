import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  FileText, Trash2, ExternalLink, RefreshCw,
  Download, FileDown
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Leads = () => {
  const { token } = useAuth();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/leads`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setLeads(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const analyseLead = async (id) => {
    setProcessingId(id);
    try {
      const res = await fetch(`${API_BASE_URL}/leads/${id}/analyse`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(await res.text());
      fetchLeads();
    } catch (e) {
      alert('Analyse fehlgeschlagen: ' + e.message);
    } finally {
      setProcessingId(null);
    }
  };

  const downloadReport = async (id, name) => {
    try {
      const res = await fetch(`${API_BASE_URL}/leads/${id}/report`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${name}_Report.pdf`;
      a.click();
    } catch (e) {
      alert('Download fehlgeschlagen: ' + e.message);
    }
  };

  const deleteLead = async (id) => {
    if (!confirm('Sicher löschen?')) return;
    try {
      await fetch(`${API_BASE_URL}/leads/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchLeads();
    } catch (e) {
      console.error(e);
    }
  };

  const StatusBadge = ({ status }) => {
    const styles = {
      neu: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
      analysiert: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      qualifiziert: 'bg-green-500/10 text-green-400 border-green-500/20',
      fehler: 'bg-red-500/10 text-red-400 border-red-500/20',
    };
    return (
      <span className={`px-2 py-1 rounded-md border text-[10px] font-bold uppercase tracking-wider ${styles[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold">Leads</h2>
          <p className="text-slate-400 mt-1">Verwalten und Analysieren Sie Ihre potenziellen Kunden</p>
        </div>
        <button className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-xl flex items-center space-x-2 transition-all">
          <Download size={18} />
          <span>Export CSV</span>
        </button>
      </header>

      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-sm uppercase tracking-wider">
                <th className="px-6 py-4 font-semibold">Unternehmen</th>
                <th className="px-6 py-4 font-semibold">Website</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold">Score</th>
                <th className="px-6 py-4 font-semibold text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-semibold text-slate-100">{lead.name}</div>
                    <div className="text-sm text-slate-500">{lead.address || 'Keine Adresse'}</div>
                  </td>
                  <td className="px-6 py-4">
                    <a href={lead.url} target="_blank" rel="noreferrer" className="text-blue-400 hover:text-blue-300 flex items-center space-x-1 text-sm transition-colors">
                      <span className="truncate max-w-[200px]">{lead.url}</span>
                      <ExternalLink size={14} />
                    </a>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={lead.status} />
                  </td>
                  <td className="px-6 py-4">
                    {lead.score_total ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-12 h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${lead.score_total > 80 ? 'bg-green-500' : lead.score_total > 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${lead.score_total}%` }}
                          />
                        </div>
                        <span className="font-mono text-sm">{lead.score_total}</span>
                      </div>
                    ) : (
                      <span className="text-slate-600 font-mono">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => analyseLead(lead.id)}
                        disabled={processingId === lead.id}
                        className="p-2 hover:bg-blue-500/10 text-blue-400 rounded-lg transition-all"
                        title="Analysieren"
                      >
                        {processingId === lead.id ? <RefreshCw className="animate-spin" size={18} /> : <FileText size={18} />}
                      </button>
                      <button
                        onClick={() => downloadReport(lead.id, lead.name)}
                        className="p-2 hover:bg-green-500/10 text-green-400 rounded-lg transition-all"
                        title="Report herunterladen"
                        disabled={!lead.score_total}
                      >
                        <FileDown size={18} />
                      </button>
                      <button
                        onClick={() => deleteLead(lead.id)}
                        className="p-2 hover:bg-red-500/10 text-red-400 rounded-lg transition-all"
                        title="Löschen"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Leads;
