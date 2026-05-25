import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Settings, LogOut, Search } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { logout } = useAuth();

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/leads', icon: Users, label: 'Leads' },
    { to: '/settings', icon: Settings, label: 'Einstellungen' },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900 flex flex-col">
      <div className="p-8">
        <h1 className="text-2xl font-bold text-blue-500">WebScore</h1>
        <p className="text-xs text-slate-500 uppercase tracking-widest mt-1">Pro Analyst</p>
      </div>

      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                isActive
                ? 'bg-blue-600/10 text-blue-500 border border-blue-600/20 shadow-[0_0_20px_rgba(37,99,235,0.1)]'
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
              }`
            }
          >
            <item.icon size={20} />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <button
          onClick={logout}
          className="flex items-center space-x-3 w-full px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-400/5 rounded-xl transition-all"
        >
          <LogOut size={20} />
          <span className="font-medium">Abmelden</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
