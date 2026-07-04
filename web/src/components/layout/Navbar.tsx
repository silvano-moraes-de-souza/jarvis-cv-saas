// ================================================================
// JARVIS CV
// ARQUIVO: Navbar.tsx
// DESCRIÇÃO: Barra de navegação premium com todas as rotas
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 3.0.0
// ================================================================
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Briefcase, Linkedin, Menu, X } from 'lucide-react';

export const Navbar = () => {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const token = localStorage.getItem('jarvis_token');

  const handleAuthClick = () => {
    setMobileOpen(false);
    if (token) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  const navLinks = [
    { to: '/', label: 'Analisador', icon: null },
    { to: '/vagas', label: 'Vagas', icon: <Briefcase size={14} /> },
    { to: '/linkedin', label: 'LinkedIn', icon: <Linkedin size={14} /> },
    { to: '/precos', label: 'Preços', icon: null },
  ];

  return (
    <nav className="fixed top-0 w-full z-50 px-4 md:px-6 py-4 md:py-6">
      <div className="max-w-6xl mx-auto flex items-center justify-between glass-panel px-4 md:px-6 py-3 rounded-full border-slate-700/50">
        <Link to="/" className="flex items-center gap-3 group cursor-pointer">
          <div className="w-9 h-9 flex items-center justify-center group-hover:rotate-12 transition-transform">
            <img
              src="https://i.ibb.co/3522fQbv/android.png"
              alt="JARVIS CV Logo"
              className="w-9 h-9 rounded-xl shadow-lg"
            />
          </div>
          <span className="font-bold tracking-tight text-xl text-white">JARVIS <span className="text-blue-500">CV</span></span>
        </Link>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
          {navLinks.map((link) => (
            <Link key={link.to} to={link.to} className="hover:text-white transition-colors relative group flex items-center gap-1">
              {link.icon}
              {link.label}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all group-hover:w-full"></span>
            </Link>
          ))}
          {token && (
            <Link to="/dashboard" className="hover:text-white transition-colors relative group">
              Dashboard
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all group-hover:w-full"></span>
            </Link>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleAuthClick}
            className="hidden md:block bg-white text-slate-950 px-6 py-2 rounded-full text-sm font-bold hover:bg-blue-50 transition-all hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] active:scale-95"
          >
            {token ? 'Dashboard' : 'Começar Agora'}
          </button>

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden text-white p-2 hover:bg-slate-800 rounded-xl transition-colors"
            aria-label={mobileOpen ? 'Fechar menu' : 'Abrir menu'}
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden mt-3 mx-4 glass-panel rounded-3xl p-6 border-slate-700/50 animate-fade-in-up">
          <div className="flex flex-col gap-4">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-2 text-base font-medium text-slate-400 hover:text-white transition-colors py-2"
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
            {token && (
              <Link
                to="/dashboard"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-2 text-base font-medium text-slate-400 hover:text-white transition-colors py-2"
              >
                Dashboard
              </Link>
            )}
            <button
              onClick={handleAuthClick}
              className="bg-white text-slate-950 px-6 py-3 rounded-xl text-sm font-bold hover:bg-blue-50 transition-all mt-2"
            >
              {token ? 'Dashboard' : 'Começar Agora'}
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};
