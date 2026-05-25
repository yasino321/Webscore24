import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Search, MapPin, Loader2, Plus } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Dashboard = () => {
  const { token } = useAuth();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState({ branche: '', ort: '' });
  const [isSearching, setIsSearching] = useState(false);

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

  const startSearch = async (e) => {
    e.preventDefault();
    setIsSearching(true);
    try {
      const res = await fetch(`${API_BASE_URL}/find-leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(search)
      });
      if (!res.ok) throw new Error(await res.text());
      fetchLeads();
    } catch (e) {
      alert(e.message);
    } finally {
      setIsSearching(false);
    }
  };

  const chartData = [
    { name: 'Sehr gut (90+)', value: leads.filter(l => l.score_total >= 90).length },
    { name: 'Gut (75-89)', value: leads.filter(l => l.score_total >= 75 && l.score_total < 90).length },
    { name: 'Mittel (60-74)', value: leads.filter(l => l.score_total >= 60 && l.score_total < 75).length },
    { name: 'Schlecht (<60)', value: leads.filter(l => l.score_total > 0 && l.score_total < 60).length },
  ];

  const statusData = [
    { name: 'Neu', value: leads.filter(l => l.status === 'neu').length },
    { name: 'Analysiert', value: leads.filter(l => l.status === 'analysiert').length },
    { name: 'Qualifiziert', value: leads.filter(l => l.status === 'qualifiziert').length },
  ];

  const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444'];
  const STATUS_COLORS = ['#94a3b8', '#3b82f6', '#22c55e'];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header>
        <h2 className="text-3xl font-bold">Dashboard</h2>
        <p className="text-slate-400 mt-1">Überblick über Ihre Lead-Aktivitäten</p>
      </header>

      <section className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl backdrop-blur-sm">
        <form onSubmit={startSearch} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input
              type="text"
              placeholder="Branche (z.B. Zahnarzt)"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-12 pr-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              value={search.branche}
              onChange={e => setSearch({...search, branche: e.target.value})}
              required
            />
          </div>
          <div className="flex-1 relative">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input
              type="text"
              placeholder="Ort (z.B. Hamburg)"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-12 pr-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              value={search.ort}
              onChange={e => setSearch({...search, ort: e.target.value})}
              required
            />
          </div>
          <button
            type="submit"
            disabled={isSearching}
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold px-8 py-3 rounded-xl transition-all flex items-center justify-center space-x-2"
          >
            {isSearching ? <Loader2 className="animate-spin" size={20} /> : <Plus size={20} />}
            <span>{isSearching ? 'Suche...' : 'Leads finden'}</span>
          </button>
        </form>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Gesamt Leads', value: leads.length, color: 'text-white' },
          { label: 'Qualifiziert', value: leads.filter(l => l.status === 'qualifiziert').length, color: 'text-green-500' },
          { label: 'Ø Score', value: leads.filter(l => l.score_total).length ? Math.round(leads.reduce((acc, l) => acc + (l.score_total || 0), 0) / (leads.filter(l => l.score_total).length || 1)) : 0, color: 'text-blue-500' },
          { label: 'Analysiert', value: leads.filter(l => l.status === 'analysiert' || l.status === 'qualifiziert').length, color: 'text-purple-500' },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
            <p className="text-sm font-medium text-slate-400">{stat.label}</p>
            <p className={`text-3xl font-bold mt-2 ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl h-[400px]">
          <h3 className="text-lg font-semibold mb-6">Score Verteilung</h3>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl h-[400px]">
          <h3 className="text-lg font-semibold mb-6">Lead Status</h3>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={STATUS_COLORS[index % STATUS_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
