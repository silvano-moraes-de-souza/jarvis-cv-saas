// ================================================================
// JARVIS CV
// ARQUIVO: DashboardPage.tsx
// DESCRIÇÃO: Dashboard premium com stats, histórico, progressão
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 3.0.0
// ================================================================
import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  FileText, Target, BarChart3, Sparkles, Crown, Zap,
  LogOut, Plus, Briefcase, TrendingUp, Search, Linkedin
} from 'lucide-react';
import { API_BASE } from '../../config';

interface UserData {
  id: string;
  email: string;
  full_name?: string;
  plan: string;
}

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserData | null>(null);
  const [resumes, setResumes] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'analyses' | 'jobs' | 'linkedin'>('overview');

  useEffect(() => {
    const token = localStorage.getItem('jarvis_token');
    const userData = localStorage.getItem('jarvis_user');

    if (!token || !userData) {
      navigate('/login');
      return;
    }

    const parsed = JSON.parse(userData);
    setUser(parsed);
    loadDashboardData(token);
  }, []);

  const loadDashboardData = async (token: string) => {
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      const [resumesRes, jobsRes] = await Promise.all([
        fetch(`${API_BASE}/resumes/`, { headers }),
        fetch(`${API_BASE}/jobs/`, { headers }),
      ]);

      if (resumesRes.ok) {
        const data = await resumesRes.json();
        setResumes(data.resumes || []);
      }
      if (jobsRes.ok) {
        const data = await jobsRes.json();
        setJobs(data.jobs || []);
      }
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jarvis_token');
    localStorage.removeItem('jarvis_user');
    navigate('/');
  };

  const planConfig: Record<string, { label: string; icon: React.ReactNode; badge: string }> = {
    elite: { label: 'Elite', icon: <Crown size={16} className="text-purple-400" />, badge: 'badge-elite' },
    pro: { label: 'Profissional', icon: <Zap size={16} className="text-blue-400" />, badge: 'badge-pro' },
    free: { label: 'Gratuito', icon: <Zap size={16} className="text-slate-400" />, badge: 'badge-free' },
  };

  const currentPlan = planConfig[user?.plan || 'free'] || planConfig.free;

  return (
    <section className="min-h-[80vh] pt-28 pb-20 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-black text-white tracking-tight">
              Olá, {user?.full_name || user?.email || 'Usuário'}
            </h1>
            <div className="flex items-center gap-2 mt-2">
              {currentPlan.icon}
              <span className="text-sm text-slate-400">Plano</span>
              <span className={`badge-plan ${currentPlan.badge}`}>{currentPlan.label}</span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="btn-ghost px-4 py-2 rounded-xl text-sm text-slate-400 hover:text-white"
          >
            <LogOut size={16} /> Sair
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <div className="stat-card">
            <FileText size={24} className="text-blue-400 mx-auto mb-2" />
            <div className="text-2xl font-black text-white">{resumes.length}</div>
            <div className="section-label mb-0">Currículos</div>
          </div>
          <div className="stat-card">
            <Briefcase size={24} className="text-indigo-400 mx-auto mb-2" />
            <div className="text-2xl font-black text-white">{jobs.length}</div>
            <div className="section-label mb-0">Vagas</div>
          </div>
          <div className="stat-card">
            <BarChart3 size={24} className="text-green-400 mx-auto mb-2" />
            <div className="text-2xl font-black text-white">0</div>
            <div className="section-label mb-0">Análises</div>
          </div>
          <div className="stat-card">
            <TrendingUp size={24} className="text-purple-400 mx-auto mb-2" />
            <div className="text-2xl font-black text-white">-</div>
            <div className="section-label mb-0">Score Médio</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-4 mb-10">
          <Link to="/" className="card-premium group cursor-pointer text-center">
            <Target size={28} className="text-blue-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="text-white font-bold mb-1">Analisar ATS</h3>
            <p className="text-slate-500 text-xs">Cole currículo + vaga e descubra seu score</p>
          </Link>

          <Link to="/vagas" className="card-premium group cursor-pointer text-center">
            <Search size={28} className="text-indigo-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="text-white font-bold mb-1">Buscar Vagas</h3>
            <p className="text-slate-500 text-xs">Encontre vagas em 9 portais com fit score</p>
          </Link>

          <Link to="/linkedin" className="card-premium group cursor-pointer text-center">
            <Linkedin size={28} className="text-purple-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="text-white font-bold mb-1">Auditoria LinkedIn</h3>
            <p className="text-slate-500 text-xs">{user?.plan === 'elite' ? 'Auditoria completa IA' : 'Requer plano Elite'}</p>
          </Link>
        </div>

        {/* Tabs */}
        <div className="flex gap-6 border-b border-slate-800 mb-8">
          {(['overview', 'analyses', 'jobs', 'linkedin'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium transition-colors ${
                activeTab === tab ? 'tab-active' : 'tab-inactive'
              }`}
            >
              {tab === 'overview' ? 'Visão Geral' :
               tab === 'analyses' ? 'Análises' :
               tab === 'jobs' ? 'Vagas' : 'LinkedIn'}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid md:grid-cols-2 gap-6">
            <div className="card-premium">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <FileText size={18} className="text-blue-400" /> Currículos
                </h3>
                <Link to="/" className="text-blue-400 text-xs font-bold hover:underline flex items-center gap-1">
                  <Plus size={14} /> Adicionar
                </Link>
              </div>
              {resumes.length === 0 ? (
                <p className="text-slate-500 text-sm">Nenhum currículo. Faça upload do seu primeiro currículo.</p>
              ) : (
                <ul className="space-y-3">
                  {resumes.map((r: any) => (
                    <li key={r.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/50 border border-slate-800">
                      <span className="text-sm text-slate-300">{r.title}</span>
                      <span className="text-xs text-slate-500">v{r.version_number}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="card-premium">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Target size={18} className="text-indigo-400" /> Vagas Alvo
                </h3>
                <Link to="/vagas" className="text-blue-400 text-xs font-bold hover:underline flex items-center gap-1">
                  <Plus size={14} /> Adicionar
                </Link>
              </div>
              {jobs.length === 0 ? (
                <p className="text-slate-500 text-sm">Nenhuma vaga. Busque vagas ou adicione manualmente.</p>
              ) : (
                <ul className="space-y-3">
                  {jobs.map((j: any) => (
                    <li key={j.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/50 border border-slate-800">
                      <span className="text-sm text-slate-300">{j.title}</span>
                      <span className="text-xs text-slate-500">{j.company || '-'}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analyses' && (
          <div className="card-premium text-center py-12">
            <BarChart3 size={48} className="text-slate-600 mx-auto mb-4" />
            <p className="text-slate-500 text-sm">Suas análises ATS aparecerão aqui.</p>
            <Link to="/" className="btn-premium premium-gradient text-white px-6 py-3 rounded-xl text-sm mt-4 inline-block">
              Fazer Primeira Análise
            </Link>
          </div>
        )}

        {activeTab === 'jobs' && (
          <div className="card-premium text-center py-12">
            <Briefcase size={48} className="text-slate-600 mx-auto mb-4" />
            <p className="text-slate-500 text-sm">Busque vagas em 9 portais com fit score.</p>
            <Link to="/vagas" className="btn-premium premium-gradient text-white px-6 py-3 rounded-xl text-sm mt-4 inline-block">
              Buscar Vagas
            </Link>
          </div>
        )}

        {activeTab === 'linkedin' && (
          <div className="card-premium text-center py-12">
            <Linkedin size={48} className="text-slate-600 mx-auto mb-4" />
            {user?.plan === 'elite' ? (
              <>
                <p className="text-slate-500 text-sm">Audite seu perfil LinkedIn com IA.</p>
                <Link to="/linkedin" className="btn-premium premium-gradient text-white px-6 py-3 rounded-xl text-sm mt-4 inline-block">
                  Iniciar Auditoria
                </Link>
              </>
            ) : (
              <>
                <p className="text-slate-500 text-sm">Auditoria LinkedIn requer plano Elite.</p>
                <Link to="/precos" className="btn-premium premium-gradient text-white px-6 py-3 rounded-xl text-sm mt-4 inline-block">
                  Fazer Upgrade
                </Link>
              </>
            )}
          </div>
        )}

        {/* Upgrade CTA */}
        {(user?.plan === 'free') && (
          <div className="mt-12 glass-panel rounded-3xl p-8 border-blue-500/30 text-center animate-pulse-glow">
            <Crown size={32} className="text-purple-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Desbloqueie todo o poder</h3>
            <p className="text-slate-400 text-sm mb-6 max-w-lg mx-auto">
              DOCX otimizado, reescrita de currículo, cartas de apresentação, estratégia semanal, auditoria LinkedIn e busca em 9 portais.
            </p>
            <div className="flex items-center justify-center gap-4">
              <Link to="/precos" className="btn-premium premium-gradient text-white px-8 py-3 rounded-xl text-sm font-bold inline-block">
                Ver Planos
              </Link>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
