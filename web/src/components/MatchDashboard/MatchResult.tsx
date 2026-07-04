// ================================================================
// JARVIS CV
// ARQUIVO: MatchResult.tsx
// DESCRIÇÃO: Resultado ATS Premium - Gauge + 6 dims PT-BR + cards com keywords
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 3.1.0
// ================================================================
import { useState, useEffect } from 'react';
import {
  CheckCircle2, XCircle, Target, Sparkles, Download,
  TrendingUp, AlertTriangle, FileCheck, Gauge, Shield,
  ChevronDown, ChevronUp, Briefcase
} from 'lucide-react';

interface MatchProps {
  score: number;
  strengths: string[];
  weaknesses: string[];
  missing_skills: string[];
  rewritten_summary: string;
  suggested_headline: string;
  improvements: string[];
  local_scores?: Record<string, number>;
  keywords_found?: string[];
  keywords_missing?: string[];
  structure_errors?: Array<{ error: string; severity: string; fix: string }>;
  sections_detected?: string[];
  seniority_detected?: string;
  seniority_alignment?: string;
  optimized_skills?: string[];
  experience_highlights?: string[];
  key_changes?: Array<{ section: string; before: string; after: string; why: string }>;
  interview_chance?: number;
  interview_factors?: Array<{ factor: string; impact: string }>;
  recruiter_verdict?: string;
  recruiter_summary?: string;
  top_3_actions?: string[];
}

const DIMENSION_LABELS: Record<string, string> = {
  keyword_match: 'Palavras-chave Encontradas',
  skill_density: 'Densidade de Habilidades',
  structure: 'Qualidade Estrutural',
  seniority: 'Alinhamento de Senioridade',
  experience_relevance: 'Relevância da Experiência',
  format: 'Compatibilidade de Formato',
};

const DIMENSION_WEIGHTS: Record<string, string> = {
  keyword_match: '30%',
  skill_density: '20%',
  structure: '15%',
  seniority: '15%',
  experience_relevance: '10%',
  format: '10%',
};

function AnimatedScore({ score }: { score: number }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const step = (timestamp: number) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(eased * score));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [score]);

  const color = score >= 70 ? 'text-green-400' : score >= 40 ? 'text-yellow-400' : 'text-red-400';
  const ringColor = score >= 70 ? '#22c55e' : score >= 40 ? '#eab308' : '#ef4444';
  const label = score >= 70 ? 'ALTA' : score >= 40 ? 'MÉDIA' : 'BAIXA';
  const labelColor = score >= 70 ? 'text-green-400' : score >= 40 ? 'text-yellow-400' : 'text-red-400';

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-44 h-44 flex items-center justify-center">
        <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r="70" fill="none" stroke="#1e293b" strokeWidth="8" />
          <circle
            cx="80" cy="80" r="70" fill="none"
            stroke={ringColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(display / 100) * 440} 440`}
            className="transition-all duration-100"
          />
        </svg>
        <div className="text-center z-10">
          <span className={`text-5xl font-black ${color}`}>{display}</span>
          <span className={`text-xl ${color} ml-0.5`}>%</span>
          <div className={`text-[10px] font-black tracking-widest ${labelColor} mt-1`}>
            PROBABILIDADE {label}
          </div>
        </div>
      </div>
    </div>
  );
}

function ScoreBar({ label, score, icon }: { label: string; score: number; icon: React.ReactNode }) {
  const color = score >= 70 ? 'bg-green-500' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-3">
      <div className="text-slate-500 w-5">{icon}</div>
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-slate-400 font-medium">{label}</span>
          <span className="text-xs text-slate-300 font-bold">{score}%</span>
        </div>
        <div className="progress-bar">
          <div className={`progress-bar-fill ${color}`} style={{ width: `${score}%` }} />
        </div>
      </div>
    </div>
  );
}

function VerdictBadge({ verdict }: { verdict: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    strong_apply: { label: 'APLIQUE FORTE', cls: 'bg-green-500/20 text-green-400 border-green-500/40' },
    apply: { label: 'APLIQUE', cls: 'bg-blue-500/20 text-blue-400 border-blue-500/40' },
    risky: { label: 'ARRISCADO', cls: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40' },
    dont_apply: { label: 'NÃO APLIQUE', cls: 'bg-red-500/20 text-red-400 border-red-500/40' },
  };
  const v = map[verdict] || { label: verdict, cls: 'bg-slate-800 text-slate-400 border-slate-700' };
  return <span className={`badge-plan ${v.cls} border`}>{v.label}</span>;
}

export const MatchResult = (props: MatchProps) => {
  const [showDetails, setShowDetails] = useState(false);
  const [showChanges, setShowChanges] = useState(false);

  const ls = props.local_scores || {};
  const hasLocal = Object.keys(ls).length > 0;

  const allFound = [...(props.keywords_found || [])];
  const allMissing = [...(props.keywords_missing || [])];

  return (
    <div className="animate-fade-in-up w-full space-y-6">
      {/* Score Principal */}
      <div className="glass-panel rounded-[40px] p-8 md:p-12">
        <div className="flex flex-col md:flex-row items-center gap-8 md:gap-12 mb-10 pb-10 border-b border-slate-800">
          <AnimatedScore score={props.score} />

          <div className="flex-1 text-center md:text-left">
            <div className="section-label">Pontuação ATS</div>
            <h2 className="text-2xl font-black text-white mb-3">
              Score: Validação Determinística Processada por IA
            </h2>
            {props.recruiter_verdict && (
              <div className="flex items-center gap-3 mb-4 justify-center md:justify-start">
                <VerdictBadge verdict={props.recruiter_verdict} />
                {props.interview_chance != null && (
                  <span className="text-sm text-slate-400">
                    Chance de entrevista: <span className="text-white font-bold">{props.interview_chance}%</span>
                  </span>
                )}
              </div>
            )}
            {props.recruiter_summary && (
              <p className="text-slate-400 text-sm leading-relaxed">{props.recruiter_summary}</p>
            )}
            {props.top_3_actions && props.top_3_actions.length > 0 && (
              <div className="mt-4 space-y-2">
                {props.top_3_actions.map((a, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-blue-400 font-bold mt-0.5">{i + 1}.</span>
                    <span className="text-slate-300">{a}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 6 Dimensões ATS */}
        {hasLocal && (
          <div className="space-y-4 mb-8">
            <div className="section-label">Score por Dimensão ATS</div>
            <div className="grid gap-3">
              <ScoreBar label={`${DIMENSION_LABELS.keyword_match} (${DIMENSION_WEIGHTS.keyword_match})`} score={ls.keyword_match || 0} icon={<Target size={14} />} />
              <ScoreBar label={`${DIMENSION_LABELS.skill_density} (${DIMENSION_WEIGHTS.skill_density})`} score={ls.skill_density || 0} icon={<Sparkles size={14} />} />
              <ScoreBar label={`${DIMENSION_LABELS.structure} (${DIMENSION_WEIGHTS.structure})`} score={ls.structure || 0} icon={<FileCheck size={14} />} />
              <ScoreBar label={`${DIMENSION_LABELS.seniority} (${DIMENSION_WEIGHTS.seniority})`} score={ls.seniority || 0} icon={<Gauge size={14} />} />
              <ScoreBar label={`${DIMENSION_LABELS.experience_relevance} (${DIMENSION_WEIGHTS.experience_relevance})`} score={ls.experience_relevance || 0} icon={<TrendingUp size={14} />} />
              <ScoreBar label={`${DIMENSION_LABELS.format} (${DIMENSION_WEIGHTS.format})`} score={ls.format || 0} icon={<Shield size={14} />} />
            </div>
          </div>
        )}

        {/* Seniority + Sections */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          {props.seniority_detected && (
            <div className="card-flat">
              <div className="section-label">Nível Detectado</div>
              <div className="flex items-center gap-3">
                <span className="text-lg font-black text-white capitalize">{props.seniority_detected}</span>
                {props.seniority_alignment && (
                  <span className={`badge-plan ${
                    props.seniority_alignment === 'match' ? 'badge-pro' :
                    props.seniority_alignment === 'underqualified' ? 'badge-elite' : 'badge-free'
                  }`}>
                    {props.seniority_alignment === 'match' ? 'ALINHADO' :
                     props.seniority_alignment === 'underqualified' ? 'SUB-QUALIFICADO' : 'SOBRE-QUALIFICADO'}
                  </span>
                )}
              </div>
            </div>
          )}
          {props.sections_detected && props.sections_detected.length > 0 && (
            <div className="card-flat">
              <div className="section-label">Seções Detectadas</div>
              <div className="flex flex-wrap gap-2">
                {props.sections_detected.map((s, i) => (
                  <span key={i} className="tag-skill tag-skill-found capitalize">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Pontos Fortes + Pontos Fracos com keywords integradas */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="p-6 rounded-3xl bg-green-500/5 border border-green-500/20">
            <div className="flex items-center gap-2 text-green-400 font-bold mb-4">
              <CheckCircle2 size={18} />
              <span>Pontos Fortes</span>
            </div>
            <ul className="space-y-2">
              {props.strengths.map((s, i) => (
                <li key={`s-${i}`} className="flex items-start gap-2 text-slate-300 text-sm leading-relaxed">
                  <CheckCircle2 size={14} className="text-green-500 shrink-0 mt-0.5" /> {s}
                </li>
              ))}
            </ul>
            {allFound.length > 0 && (
              <>
                <div className="text-xs text-green-500/70 font-bold uppercase tracking-wider mt-5 mb-3">
                  Palavras-chave Encontradas ({allFound.length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {allFound.map((kw, i) => (
                    <span key={`fk-${i}`} className="tag-skill tag-skill-found text-[10px]">
                      <CheckCircle2 size={10} className="inline mr-1" />{kw}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>

          <div className="p-6 rounded-3xl bg-red-500/5 border border-red-500/20">
            <div className="flex items-center gap-2 text-red-400 font-bold mb-4">
              <XCircle size={18} />
              <span>Pontos Fracos</span>
            </div>
            <ul className="space-y-2">
              {props.weaknesses.map((w, i) => (
                <li key={`w-${i}`} className="flex items-start gap-2 text-slate-300 text-sm leading-relaxed">
                  <XCircle size={14} className="text-red-500 shrink-0 mt-0.5" /> {w}
                </li>
              ))}
            </ul>
            {allMissing.length > 0 && (
              <>
                <div className="text-xs text-red-500/70 font-bold uppercase tracking-wider mt-5 mb-3">
                  Palavras-chave Faltantes ({allMissing.length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {allMissing.map((kw, i) => (
                    <span key={`mk-${i}`} className="tag-skill tag-skill-missing text-[10px]">
                      <XCircle size={10} className="inline mr-1" />{kw}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Structure Errors */}
        {props.structure_errors && props.structure_errors.length > 0 && (
          <div className="mb-8">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
            >
              <AlertTriangle size={14} className="text-yellow-400" />
              <span>{props.structure_errors.length} problema(s) de estrutura</span>
              {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            {showDetails && (
              <div className="mt-3 space-y-2 animate-fade-in">
                {props.structure_errors.map((err, i) => (
                  <div key={i} className="card-flat p-3 flex items-start gap-3">
                    <span className={`shrink-0 w-2 h-2 rounded-full mt-1.5 ${
                      err.severity === 'high' ? 'bg-red-500' : err.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                    }`} />
                    <div>
                      <p className="text-sm text-slate-300">{err.error}</p>
                      {err.fix && <p className="text-xs text-slate-500 mt-1">Correção: {err.fix}</p>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Headline + Summary + Plano de Ação */}
      <div className="glass-panel rounded-[40px] p-8 md:p-12">
        <div className="p-8 rounded-3xl bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border border-blue-500/30 mb-8">
          <div className="flex items-center gap-2 text-blue-400 font-bold mb-4">
            <Sparkles size={18} />
            <span>Headline de Alta Conversão</span>
          </div>
          {props.suggested_headline ? (
            <p className="text-xl md:text-2xl font-black text-white tracking-tight leading-tight">
              {props.suggested_headline}
            </p>
          ) : (
            <p className="text-sm text-slate-500 italic">
              A IA não conseguiu gerar uma headline específica. Tente adicionar mais palavras-chave ao seu currículo.
            </p>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="card-flat">
            <div className="section-label">Resumo Profissional Otimizado</div>
            {props.rewritten_summary ? (
              <p className="text-slate-300 text-sm leading-relaxed italic">
                "{props.rewritten_summary}"
              </p>
            ) : (
              <p className="text-sm text-slate-500 italic">
                Não foi possível gerar um resumo otimizado. Forneça mais detalhes sobre suas conquistas.
              </p>
            )}
          </div>
          <div className="card-flat">
            <div className="section-label">Plano de Ação</div>
            {props.improvements && props.improvements.length > 0 ? (
              <ul className="space-y-2">
                {props.improvements.map((imp, i) => (
                  <li key={i} className="text-slate-400 text-sm flex gap-2">
                    <span className="text-blue-500 shrink-0">•</span> {imp}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500 italic">
                Nenhuma recomendação específica foi gerada para este perfil.
              </p>
            )}
          </div>
        </div>

        {/* Optimized Skills */}
        {props.optimized_skills && props.optimized_skills.length > 0 && (
          <div className="mb-8">
            <div className="section-label">Habilidades Otimizadas</div>
            <div className="flex flex-wrap gap-2">
              {props.optimized_skills.map((skill, i) => (
                <span key={i} className="tag-skill tag-skill-neutral">{skill}</span>
              ))}
            </div>
          </div>
        )}

        {/* Experience Highlights */}
        {props.experience_highlights && props.experience_highlights.length > 0 && (
          <div className="mb-8">
            <div className="section-label">Destaques de Experiência</div>
            <ul className="space-y-2">
              {props.experience_highlights.map((h, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                  <Briefcase size={14} className="text-indigo-400 shrink-0 mt-0.5" />
                  {h}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Key Changes */}
        {props.key_changes && props.key_changes.length > 0 && (
          <div>
            <button
              onClick={() => setShowChanges(!showChanges)}
              className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
            >
              <Sparkles size={14} className="text-blue-400" />
              <span>{props.key_changes.length} mudança(s) otimizada(s)</span>
              {showChanges ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            {showChanges && (
              <div className="mt-3 space-y-4 animate-fade-in">
                {props.key_changes.map((c, i) => (
                  <div key={i} className="card-flat p-4">
                    <p className="text-sm font-bold text-blue-400 mb-2">{c.section}</p>
                    {c.before && <p className="text-xs text-slate-500 italic">Antes: {c.before}</p>}
                    {c.after && <p className="text-xs text-slate-300 font-medium mt-1">Depois: {c.after}</p>}
                    {c.why && <p className="text-xs text-slate-500 mt-1">Por quê: {c.why}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Interview Factors */}
      {props.interview_factors && props.interview_factors.length > 0 && (
        <div className="glass-panel rounded-[40px] p-8">
          <div className="section-label">Fatores de Chance de Entrevista</div>
          <div className="grid gap-2">
            {props.interview_factors.map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full shrink-0 ${
                  f.impact === 'positive' ? 'bg-green-500' :
                  f.impact === 'negative' ? 'bg-red-500' : 'bg-slate-500'
                }`} />
                <span className="text-sm text-slate-300">{f.factor}</span>
                <span className={`text-[10px] font-bold uppercase ml-auto ${
                  f.impact === 'positive' ? 'text-green-400' :
                  f.impact === 'negative' ? 'text-red-400' : 'text-slate-500'
                }`}>{f.impact}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};