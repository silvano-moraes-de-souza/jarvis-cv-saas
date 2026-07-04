// ================================================================
// JARVIS CV
// ARQUIVO: App.tsx
// DESCRIÇÃO: Componente principal - Roteamento + Analyzer com extração de CV/Job
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 3.2.0
// ================================================================
import { useState, useRef, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { NotFound } from './components/layout/NotFound';
import { Hero } from './components/home/Hero';
import { MatchResult } from './components/MatchDashboard/MatchResult';
import { PricingPage } from './components/pricing/PricingPage';
import { AuthPage } from './components/auth/AuthPage';
import { DashboardPage } from './components/dashboard/DashboardPage';
import { JobSearchPage } from './components/jobs/JobSearchPage';
import { LinkedInAuditPage } from './components/linkedin/LinkedInAuditPage';
import { Upload, FileText, Briefcase, Download, Sparkles, Loader2, Link as LinkIcon, CheckCircle2 } from 'lucide-react';
import { API_BASE } from './config';

const PROGRESS_MESSAGES = [
  'Conectando ao servidor...',
  'Calculando score ATS local...',
  'Extraindo palavras-chave da vaga...',
  'Detectando seções do currículo...',
  'Analisando compatibilidade com a vaga...',
  'Enviando para análise de IA...',
  'Processando resultados...',
  'Gerando recomendações...',
];

function AnalyzerPage() {
  const navigate = useNavigate();
  const [cv, setCv] = useState('');
  const [job, setJob] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [extractingCv, setExtractingCv] = useState(false);
  const [extractingJob, setExtractingJob] = useState(false);
  const [jobLoaded, setJobLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadingDocx, setDownloadingDocx] = useState(false);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [progressMsg, setProgressMsg] = useState('');
  const resultRef = useRef<HTMLDivElement>(null);
  const startTimeRef = useRef<number>(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const msgIndexRef = useRef(0);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const formatTime = useCallback((ms: number) => {
    const totalSec = Math.floor(ms / 1000);
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    return `${m}m ${s.toString().padStart(2, '0')}s`;
  }, []);

  const startProgressTimer = () => {
    startTimeRef.current = Date.now();
    msgIndexRef.current = 0;
    setElapsedMs(0);
    setProgressMsg(PROGRESS_MESSAGES[0]);

    // Update elapsed time every 100ms
    timerRef.current = setInterval(() => {
      setElapsedMs(Date.now() - startTimeRef.current);

      // Rotate messages every 3 seconds
      const elapsed = Date.now() - startTimeRef.current;
      const newMsgIdx = Math.min(
        Math.floor(elapsed / 3000),
        PROGRESS_MESSAGES.length - 1
      );
      if (newMsgIdx !== msgIndexRef.current) {
        msgIndexRef.current = newMsgIdx;
        setProgressMsg(PROGRESS_MESSAGES[newMsgIdx]);
      }
    }, 100);
  };

  const stopProgressTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setExtractingCv(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/analysis/extract-cv`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Erro ao extrair texto do arquivo.');
      const data = await response.json();
      setCv(data.text);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setExtractingCv(false);
    }
  };

  const handleExtractJob = async () => {
    if (!jobUrl.trim()) return;
    setExtractingJob(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/analysis/extract-job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: jobUrl }),
      });
      if (!response.ok) throw new Error('Não foi possível extrair a vaga desta URL.');
      const data = await response.json();
      setJob(data.text);
      setJobLoaded(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setExtractingJob(false);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    startProgressTimer();

    try {
      const response = await fetch(`${API_BASE}/analysis/ats/raw`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cv_text: cv, job_text: job }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro na análise do servidor.');
      }

      const data = await response.json();
      stopProgressTimer();
      setProgressMsg('Análise concluída!');
      setResult(data);
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 300);
    } catch (err: any) {
      stopProgressTimer();
      setError(`Erro de Conexão: ${err.message}. Verifique se o backend está rodando em http://localhost:3001`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadDocx = async () => {
    if (!result) return;
    setDownloadingDocx(true);
    try {
      const response = await fetch(`${API_BASE}/analysis/ats/raw/docx`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cv_text: cv, job_text: job }),
      });

      if (!response.ok) throw new Error('Erro ao gerar DOCX');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Curriculo_Otimizado_JARVIS_CV.docx';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('DOCX Error:', err);
    } finally {
      setDownloadingDocx(false);
    }
  };

  return (
    <section id="analyzer" className="max-w-6xl mx-auto px-6 pb-32">
      <div className="grid md:grid-cols-2 gap-6 mb-10">
        <div className="card-premium">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <span className="w-2 h-5 bg-blue-500 rounded-full"></span>
              <FileText size={18} className="text-blue-400" /> Seu Currículo
            </h3>
            <label className="cursor-pointer flex items-center gap-2 text-xs font-bold text-blue-400 hover:text-blue-300 transition-all bg-blue-500/10 px-3 py-1.5 rounded-lg border border-blue-500/20">
              {extractingCv ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
              Upload PDF/Word
              <input type="file" className="hidden" accept=".pdf,.docx" onChange={handleFileUpload} />
            </label>
          </div>
          <textarea
            value={cv}
            onChange={(e) => setCv(e.target.value)}
            placeholder="Cole aqui seu currículo completo ou faça upload..."
            className="w-full h-72 bg-slate-950/50 border border-slate-800 rounded-2xl p-5 resize-none focus:border-blue-500 outline-none transition-all placeholder:text-slate-600 text-sm leading-relaxed"
          />
          <div className="flex items-center justify-between mt-2">
            <span className="text-[10px] text-slate-600">{cv.length} caracteres</span>
            {cv.length > 0 && cv.length < 200 && (
              <span className="text-[10px] text-yellow-500 font-bold">Mínimo 200 caracteres</span>
            )}
          </div>
        </div>

        <div className="card-premium">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <span className="w-2 h-5 bg-indigo-500 rounded-full"></span>
              <Briefcase size={18} className="text-indigo-400" /> Descrição da Vaga
            </h3>
            <div className="flex items-center gap-2">
              <input 
                type="text" 
                value={jobUrl} 
                onChange={(e) => setJobUrl(e.target.value)}
                placeholder="Link da vaga..."
                className="bg-slate-950/50 border border-slate-800 rounded-lg px-3 py-1 text-[10px] text-white focus:border-indigo-500 outline-none w-32"
              />
              <button 
                onClick={handleExtractJob}
                disabled={extractingJob || !jobUrl.trim()}
                className="flex items-center gap-1 text-xs font-bold text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 px-3 py-1.5 rounded-lg border border-indigo-500/20 transition-all disabled:opacity-50"
              >
                {extractingJob ? <Loader2 size={14} className="animate-spin" /> : <LinkIcon size={14} />}
                Extrair
              </button>
            </div>
          </div>
          <textarea
            value={job}
            onChange={(e) => setJob(e.target.value)}
            placeholder="Cole aqui a descrição da vaga ou use o link acima..."
            className="w-full h-72 bg-slate-950/50 border border-slate-800 rounded-2xl p-5 resize-none focus:border-blue-500 outline-none transition-all placeholder:text-slate-600 text-sm leading-relaxed"
          />
          <div className="flex items-center justify-between mt-2">
            <span className="text-[10px] text-slate-600">{job.length} caracteres</span>
            {jobLoaded && (
              <span className="text-[10px] text-green-500 font-bold flex items-center gap-1">
                <CheckCircle2 size={10} /> Informações carregadas com sucesso
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="flex flex-col items-center gap-4">
        <button
          onClick={handleAnalyze}
          disabled={loading || !cv || !job || cv.length < 200}
          className="btn-premium premium-gradient text-white px-12 py-5 rounded-2xl text-xl font-black shadow-2xl shadow-blue-500/20 hover:scale-105 transition-all disabled:opacity-50 disabled:scale-100 disabled:hover:shadow-blue-500/20"
        >
          {loading ? (
            <span className="flex items-center gap-3">
              <Loader2 size={22} className="animate-spin" /> Processando...
            </span>
          ) : (
            <span className="flex items-center gap-3">
              <Sparkles size={22} /> Analise Agora é Grátis
            </span>
          )}
        </button>

        {loading && (
          <div className="w-full max-w-lg animate-fade-in-up">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Loader2 size={14} className="animate-spin text-blue-400" />
                <span className="text-xs text-slate-400 font-medium">{progressMsg}</span>
              </div>
              <span className="text-xs text-blue-400 font-bold tabular-nums font-mono">
                {formatTime(elapsedMs)}
              </span>
            </div>
            {/* Animated pulse bar (no fake percentage) */}
            <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full rounded-full premium-gradient animate-pulse"
                style={{ width: '60%' }}
              />
            </div>
          </div>
        )}

        {!loading && (
          <p className="text-xs text-slate-600 text-center whitespace-nowrap">
            Score híbrido: 40% motor local determinístico (6 dimensões) + 60% IA de última geração
          </p>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 text-red-400 rounded-2xl border border-red-500/20 text-center animate-fade-in-up mt-8">
          {error}
        </div>
      )}

      {result && (
        <div ref={resultRef} className="mt-12 animate-fade-in-up">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-black text-white">Resultado da Análise</h2>
            <button
              onClick={handleDownloadDocx}
              disabled={downloadingDocx}
              className="btn-ghost px-4 py-2 rounded-xl text-sm text-green-400 hover:text-green-300"
            >
              {downloadingDocx ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />} Baixar DOCX
            </button>
          </div>
          <MatchResult
            score={result.ats_score ?? result.score ?? 0}
            strengths={result.strengths || []}
            weaknesses={result.weaknesses || []}
            missing_skills={result.missing_skills || []}
            rewritten_summary={result.rewritten_summary || ''}
            suggested_headline={result.suggested_headline || ''}
            improvements={result.recommendations || []}
            local_scores={result.local_scores || {}}
            keywords_found={result.keywords_found || []}
            keywords_missing={result.keywords_missing || []}
            structure_errors={result.structure_errors || []}
            sections_detected={result.sections_detected || []}
            seniority_detected={result.seniority_detected || ''}
            seniority_alignment={result.seniority_alignment || ''}
            optimized_skills={result.optimized_skills || []}
            experience_highlights={result.experience_highlights || []}
            key_changes={result.key_changes || []}
            interview_chance={result.interview_chance}
            interview_factors={result.interview_factors || []}
            recruiter_verdict={result.recruiter_verdict || ''}
            recruiter_summary={result.recruiter_summary || ''}
            top_3_actions={result.top_3_actions || []}
          />
        </div>
      )}
    </section>
  );
}

function LandingPage() {
  return (
    <main>
      <Hero />
      <AnalyzerPage />
    </main>
  );
}

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-slate-950 text-white selection:bg-blue-500/30 flex flex-col">
        <Navbar />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<AuthPage mode="login" />} />
            <Route path="/registro" element={<AuthPage mode="register" />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/vagas" element={<JobSearchPage />} />
            <Route path="/linkedin" element={<LinkedInAuditPage />} />
            <Route path="/precos" element={<PricingPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
        <footer className="border-t border-slate-900 py-6 text-center text-slate-500 text-sm">
          © 2026 JARVIS CV. Criado por <span className="text-slate-300 font-medium">Silvano Moraes de Souza</span>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;