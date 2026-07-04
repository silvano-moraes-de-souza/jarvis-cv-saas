// ================================================================
// JARVIS CV
// ARQUIVO: AuthPage.tsx
// DESCRIÇÃO: Página de autenticação - Login e Registro com design premium
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 2.0.0
// ================================================================
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, Mail, Lock, User, Eye, EyeOff } from 'lucide-react';
import { API_BASE } from '../../config';

interface AuthPageProps {
  mode: 'login' | 'register';
}

export const AuthPage = ({ mode }: AuthPageProps) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const isLogin = mode === 'login';

  const passwordStrength = (pw: string): { score: number; label: string; color: string } => {
    if (!pw) return { score: 0, label: '', color: 'bg-slate-700' };
    let s = 0;
    if (pw.length >= 8) s++;
    if (pw.length >= 12) s++;
    if (/[A-Z]/.test(pw)) s++;
    if (/[0-9]/.test(pw)) s++;
    if (/[^A-Za-z0-9]/.test(pw)) s++;
    if (s <= 1) return { score: 20, label: 'Fraca', color: 'bg-red-500' };
    if (s <= 2) return { score: 40, label: 'Média', color: 'bg-yellow-500' };
    if (s <= 3) return { score: 70, label: 'Boa', color: 'bg-blue-500' };
    return { score: 100, label: 'Forte', color: 'bg-green-500' };
  };

  const strength = passwordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const body = isLogin
        ? { email, password }
        : { email, password, full_name: fullName, accept_terms: true };

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Erro na autenticação.');
      }

      const data = await response.json();
      localStorage.setItem('jarvis_token', data.access_token);
      localStorage.setItem('jarvis_user', JSON.stringify(data.user));
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-6 pt-24">
      <div className="glow-effect w-[400px] h-[400px] bg-blue-600 top-[10%] left-[20%] opacity-20" />

      <div className="w-full max-w-md glass-panel rounded-3xl p-8 border-slate-800/60 relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold mb-6">
            <Sparkles size={14} />
            <span>{isLogin ? 'Bem-vindo de volta' : 'Crie sua conta'}</span>
          </div>
          <h2 className="text-3xl font-black text-white tracking-tight">
            {isLogin ? 'Entrar' : 'Registro'}
          </h2>
          <p className="text-slate-400 text-sm mt-2">
            {isLogin ? 'Acesse sua conta JARVIS CV' : 'Comece a otimizar sua carreira agora'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {!isLogin && (
<div className="relative">
            <User size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Nome completo"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="w-full pl-12 pr-4 py-3.5 bg-slate-950/50 border border-slate-800 rounded-xl text-white placeholder:text-slate-600 focus:border-blue-500 outline-none transition-all text-sm"
            />
          </div>
          )}

          <div className="relative">
            <Mail size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full pl-12 pr-4 py-3.5 bg-slate-950/50 border border-slate-800 rounded-xl text-white placeholder:text-slate-600 focus:border-blue-500 outline-none transition-all text-sm"
            />
          </div>

          <div className="relative">
            <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Senha"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full pl-12 pr-12 py-3.5 bg-slate-950/50 border border-slate-800 rounded-xl text-white placeholder:text-slate-600 focus:border-blue-500 outline-none transition-all text-sm"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
              aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {!isLogin && password.length > 0 && (
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Força da senha</span>
                <span className="font-bold text-slate-300">{strength.label}</span>
              </div>
              <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${strength.color}`}
                  style={{ width: `${strength.score}%` }}
                />
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-500/10 text-red-400 rounded-xl border border-red-500/20 text-sm text-center">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-premium premium-gradient text-white py-4 rounded-xl text-base font-bold shadow-xl shadow-blue-500/20 hover:scale-[1.02] transition-all disabled:opacity-50"
          >
            {loading ? 'Processando...' : isLogin ? 'Entrar' : 'Criar Conta'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          {isLogin ? (
            <span>Não tem conta? <Link to="/registro" className="text-blue-400 font-bold hover:underline">Registre-se</Link></span>
          ) : (
            <span>Já tem conta? <Link to="/login" className="text-blue-400 font-bold hover:underline">Entrar</Link></span>
          )}
        </div>
      </div>
    </div>
  );
};
