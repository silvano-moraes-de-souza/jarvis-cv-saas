// ================================================================
// JARVIS CV
// ARQUIVO: JobSearchPage.tsx
// DESCRIÇÃO: Busca de vagas em 9 portais com fit score + cards premium
//            Remoto/Híbrido/Presencial toggle + raio + legenda fit
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 3.1.0
// ================================================================
import { useState } from 'react';
import { Search, Briefcase, MapPin, DollarSign, ExternalLink, Globe, Building2, Wifi, Radio } from 'lucide-react';
import { API_BASE } from '../../config';

type WorkMode = 'remote' | 'hybrid' | 'onsite';

const WORK_MODE_CONFIG: Record<WorkMode, { label: string; icon: React.ReactNode; radiusKm: number; radiusLabel: string; color: string; activeColor: string }> = {
  remote: {
    label: 'Remoto',
    icon: <Globe size={14} />,
    radiusKm: 0,
    radiusLabel: 'Brasil (sem limite)',
    color: 'bg-green-500/10 text-green-400 border-green-500/30',
    activeColor: 'bg-green-500/20 text-green-300 border-green-400',
  },
  hybrid: {
    label: 'Híbrido',
    icon: <Wifi size={14} />,
    radiusKm: 100,
    radiusLabel: '100 km da localização',
    color: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    activeColor: 'bg-blue-500/20 text-blue-300 border-blue-400',
  },
  onsite: {
    label: 'Presencial',
    icon: <Building2 size={14} />,
    radiusKm: 50,
    radiusLabel: '50 km da localização',
    color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    activeColor: 'bg-amber-500/20 text-amber-300 border-amber-400',
  },
};

const FIT_LABELS: Record<string, { label: string; description: string; color: string }> = {
  alto: { label: 'Alto', description: 'Seu perfil atende 70%+ dos requisitos', color: 'text-green-400' },
  medio: { label: 'Médio', description: 'Seu perfil atende 40-69% dos requisitos', color: 'text-yellow-400' },
  baixo: { label: 'Baixo', description: 'Seu perfil atende menos de 40% dos requisitos', color: 'text-red-400' },
};

interface JobResult {
  title: string;
  company: string;
  location: string;
  salary_range: string;
  is_remote: boolean;
  url: string;
  source: string;
  description: string;
  fit_score: number;
  application_difficulty: string;
  attack_priority: number;
}

export const JobSearchPage = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [workMode, setWorkMode] = useState<WorkMode>('remote');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<JobResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [portalsSearched, setPortalsSearched] = useState<string[]>([]);
  const [showLegend, setShowLegend] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('jarvis_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const endpoint = token ? '/jobs/search' : '/jobs/search/raw';
      const modeConfig = WORK_MODE_CONFIG[workMode];

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query,
          location,
          remote: workMode === 'remote',
          work_mode: workMode,
          radius_km: modeConfig.radiusKm,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Erro na busca');
      }

      const data = await response.json();
      setResults(data.jobs || []);
      setPortalsSearched(data.portals_searched || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fitColor = (score: number) =>
    score >= 70 ? 'text-green-400' : score >= 40 ? 'text-yellow-400' : 'text-red-400';

  const fitBg = (score: number) =>
    score >= 70 ? 'bg-green-500/10 border-green-500/30' : score >= 40 ? 'bg-yellow-500/10 border-yellow-500/30' : 'bg-red-500/10 border-red-500/30';

  const fitLabel = (score: number) =>
    score >= 70 ? 'Alto' : score >= 40 ? 'Médio' : 'Baixo';

  const difficultyLabel: Record<string, string> = {
    easy: 'Fácil',
    moderate: 'Moderado',
    hard: 'Difícil',
    very_hard: 'Muito Difícil',
  };

  const difficultyColor: Record<string, string> = {
    easy: 'badge-pro',
    moderate: 'badge-free',
    hard: 'badge-elite',
    very_hard: 'bg-red-500/20 text-red-400 border-red-500/30',
  };

  return (
    <section className="pt-28 pb-20 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <h1 className="text-3xl font-black text-white tracking-tight mb-2">Buscar Vagas</h1>
          <p className="text-slate-400 text-sm">Encontre vagas em 9 portais com compatibilidade calculada para seu perfil</p>
        </div>

        {/* Search Bar */}
        <div className="glass-panel rounded-3xl p-6 mb-8">
          <div className="grid md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <label className="section-label">Buscar</label>
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Ex: analista de dados, python, power bi..."
                className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all placeholder:text-slate-600"
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div>
              <label className="section-label">Localização</label>
              <input
                value={location}
                onChange={e => setLocation(e.target.value)}
                placeholder={workMode === 'remote' ? 'Opcional (Remoto)' : 'São Paulo, SP...'}
                className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all placeholder:text-slate-600"
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div className="flex flex-col justify-end">
              <button
                onClick={handleSearch}
                disabled={loading || !query.trim()}
                className="btn-premium premium-gradient text-white px-6 py-3 rounded-xl text-sm disabled:opacity-50"
              >
                {loading ? (
                  <span className="animate-shimmer">Buscando...</span>
                ) : (
                  <><Search size={16} /> Buscar Vagas</>
                )}
              </button>
            </div>
          </div>

          {/* Work Mode Toggle */}
          <div className="flex flex-col sm:flex-row sm:items-center gap-4 mt-5">
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mr-1">Modalidade:</span>
              {(Object.keys(WORK_MODE_CONFIG) as WorkMode[]).map(mode => {
                const cfg = WORK_MODE_CONFIG[mode];
                const active = workMode === mode;
                return (
                  <button
                    key={mode}
                    onClick={() => setWorkMode(mode)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
                      active ? cfg.activeColor : 'bg-slate-950/50 text-slate-500 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    {cfg.icon} {cfg.label}
                  </button>
                );
              })}
            </div>

            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <Radio size={12} className={workMode === 'remote' ? 'text-green-400' : workMode === 'hybrid' ? 'text-blue-400' : 'text-amber-400'} />
                Raio: <span className="text-slate-300 font-bold">{WORK_MODE_CONFIG[workMode].radiusLabel}</span>
              </span>
            </div>

            {portalsSearched.length > 0 && (
              <span className="text-xs text-slate-500 sm:ml-auto">
                Buscado em: {portalsSearched.join(', ')}
              </span>
            )}
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-500/10 text-red-400 rounded-2xl border border-red-500/20 text-center text-sm mb-8 animate-fade-in-up">
            {error}
          </div>
        )}

        {/* Results Header + Legend Toggle */}
        {results.length > 0 && (
          <div className="mb-4 flex items-center justify-between">
            <span className="text-sm text-slate-400">{results.length} vagas encontradas</span>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowLegend(!showLegend)}
                className="text-xs text-slate-500 hover:text-slate-300 transition-colors underline underline-offset-2"
              >
                {showLegend ? 'Ocultar legenda' : 'O que significa a compatibilidade?'}
              </button>
              <span className="text-xs text-slate-500">Ordenado por compatibilidade</span>
            </div>
          </div>
        )}

        {/* Legend */}
        {showLegend && (
          <div className="glass-panel rounded-2xl p-5 mb-6 animate-fade-in">
            <div className="section-label mb-3">Legenda de Compatibilidade</div>
            <div className="grid sm:grid-cols-3 gap-4">
              {Object.entries(FIT_LABELS).map(([key, cfg]) => (
                <div key={key} className="flex items-start gap-2">
                  <span className={`w-3 h-3 rounded-full shrink-0 mt-0.5 ${
                    key === 'alto' ? 'bg-green-500' : key === 'medio' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className={`text-sm font-bold ${cfg.color}`}>{cfg.label}</p>
                    <p className="text-xs text-slate-500">{cfg.description}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800">
              <div className="section-label mb-2">Dificuldade de Candidatura</div>
              <div className="flex flex-wrap gap-3">
                <span className="badge-plan badge-pro text-[10px]">Fácil: poucos candidatos, alta chance</span>
                <span className="badge-plan badge-free text-[10px]">Moderado: competição normal</span>
                <span className="badge-plan badge-elite text-[10px]">Difícil: muitos candidatos qualificados</span>
                <span className="badge-plan bg-red-500/20 text-red-400 border border-red-500/30 text-[10px]">Muito Difícil: alta competição</span>
              </div>
            </div>
          </div>
        )}

        {/* Job Cards */}
        <div className="grid gap-4">
          {results.map((job, i) => (
            <div
              key={i}
              className="card-premium flex flex-col md:flex-row md:items-center gap-4 animate-fade-in-up"
              style={{ animationDelay: `${i * 50}ms` }}
            >
              {/* Fit Score */}
              <div className={`shrink-0 w-16 h-16 rounded-2xl flex flex-col items-center justify-center border ${fitBg(job.fit_score)}`}>
                <span className={`text-lg font-black ${fitColor(job.fit_score)}`}>
                  {job.fit_score > 0 ? Math.round(job.fit_score) : '-'}
                </span>
                <span className={`text-[9px] font-bold ${fitColor(job.fit_score)}`}>
                  {job.fit_score > 0 ? fitLabel(job.fit_score) : 'SEM FIT'}
                </span>
              </div>

              {/* Job Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-white font-bold text-sm truncate">{job.title}</h3>
                  {job.is_remote && (
                    <span className="badge-plan badge-pro text-[9px]">REMOTO</span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-500">
                  <span className="flex items-center gap-1"><Briefcase size={12} /> {job.company || '-'}</span>
                  <span className="flex items-center gap-1"><MapPin size={12} /> {job.location || '-'}</span>
                  {job.salary_range && <span className="flex items-center gap-1"><DollarSign size={12} /> {job.salary_range}</span>}
                </div>
                {job.description && (
                  <p className="text-xs text-slate-600 mt-1 line-clamp-2">{job.description}</p>
                )}
              </div>

              {/* Meta */}
              <div className="shrink-0 flex items-center gap-3">
                <span className="text-[10px] text-slate-500 uppercase font-bold">{job.source}</span>
                <span className={`badge-plan ${difficultyColor[job.application_difficulty] || 'badge-free'}`}>
                  {difficultyLabel[job.application_difficulty] || job.application_difficulty}
                </span>
                {job.url && (
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-premium glass-panel text-blue-400 px-3 py-1.5 rounded-lg text-xs hover:text-white"
                  >
                    <ExternalLink size={12} /> Ver
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {results.length === 0 && !loading && !error && query && (
          <div className="text-center py-16">
            <Search size={48} className="text-slate-700 mx-auto mb-4" />
            <p className="text-slate-500 text-sm">Busque vagas para ver resultados</p>
          </div>
        )}
      </div>
    </section>
  );
};