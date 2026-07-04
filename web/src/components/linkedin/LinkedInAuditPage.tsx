// ================================================================
// JARVIS CV
// ARQUIVO: LinkedInAuditPage.tsx
// DESCRIÇÃO: Auditoria LinkedIn - Extração via browser do usuário + IA
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 5.0.0
// ================================================================
import { useState, useRef, useEffect } from 'react';
import {
  Linkedin, AlertTriangle, XCircle, Sparkles, Lightbulb,
  Link2, FileText, Copy, Check, Terminal, ExternalLink, ChevronDown, ChevronUp
} from 'lucide-react';
import { API_BASE } from '../../config';

interface AuditResult {
  overall_score: number;
  scores: Record<string, number>;
  issues: Array<{ error: string; fix: string }>;
  quick_wins: Array<{ action: string; impact: string; effort: string }>;
  ai_audit?: any;
  scrape_failed?: boolean;
}

type InputMode = 'url' | 'extractor' | 'manual';

const EXTRACTOR_SCRIPT = `
(function() {
  const overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);z-index:99999;display:flex;align-items:center;justify-content:center;font-family:system-ui,sans-serif;';
  overlay.innerHTML = '<div style="background:#0f172a;border:1px solid #334155;border-radius:16px;padding:24px;max-width:500px;width:90%;max-height:80vh;overflow-y:auto;color:#e2e8f0;"><h2 style="color:#60a5fa;margin:0 0 8px;font-size:18px;">⚡ JARVIS CV - Extraindo dados...</h2><p style="color:#94a3b8;font-size:13px;margin:0 0 16px;" id="li-status">Coletando informações do perfil...</p><div style="background:#1e293b;border-radius:8px;padding:12px;font-size:12px;color:#64748b;max-height:200px;overflow-y:auto;white-space:pre-wrap;font-family:monospace;" id="li-log"></div></div>';
  document.body.appendChild(overlay);

  const log = (msg) => { const el = document.getElementById('li-log'); if(el) el.textContent += msg + '\\n'; };
  const status = (msg) => { const el = document.getElementById('li-status'); if(el) el.textContent = msg; };

  setTimeout(() => {
    // Scroll to load lazy content
    window.scrollTo(0, document.body.scrollHeight);
    log('Scroll para carregar conteúdo...');

    setTimeout(() => {
      const data = {};

      // Headline
      const hl = document.querySelector('.text-body-medium');
      data.headline = (hl && hl.innerText.length > 5) ? hl.innerText.trim() : '';
      if (!data.headline) {
        const h1 = document.querySelector('h1');
        if (h1 && h1.nextElementSibling) {
          const nxt = h1.nextElementSibling;
          if (nxt.innerText.length > 10 && nxt.innerText.length < 300) data.headline = nxt.innerText.trim();
        }
      }
      log('Headline: ' + (data.headline ? data.headline.substring(0, 50) + '...' : 'NÃO ENCONTRADA'));

      // About
      const allText = document.body.innerText;
      const aboutMatch = allText.match(/Sobre\\s*\\n([\\s\\S]{50,}?)(?=\\n\\s*(?:Experiência|Atividade|Competências|Destaques))/i);
      data.about = aboutMatch ? aboutMatch[1].trim() : '';
      log('About: ' + (data.about ? data.about.substring(0, 50) + '...' : 'NÃO ENCONTRADO'));

      // Experience
      const expMatch = allText.match(/Experiência\\s*\\n([\\s\\S]{100,}?)(?=\\n\\s*(?:Formação|Competências|Idiomas))/i);
      data.experience = expMatch ? expMatch[1].trim() : '';
      log('Experience: ' + (data.experience ? data.experience.substring(0, 50) + '...' : 'NÃO ENCONTRADA'));

      // Navigate to skills
      status('Extraindo skills...');
      const skillsLink = Array.from(document.querySelectorAll('a')).find(a => a.href && a.href.includes('/details/skills/'));
      if (skillsLink) {
        skillsLink.click();
        log('Navegando para skills...');

        setTimeout(() => {
          window.scrollTo(0, document.body.scrollHeight);
          setTimeout(() => {
            window.scrollTo(0, document.body.scrollHeight);
            setTimeout(() => {
              const skillsSet = new Set();
              const editLinks = document.querySelectorAll('a[href*="/skills/edit/forms/"]');
              editLinks.forEach(link => {
                const parent = link.parentElement;
                if (parent) {
                  const texts = Array.from(parent.childNodes)
                    .filter(n => n.nodeType === 3 && n.textContent.trim().length > 1)
                    .map(n => n.textContent.trim());
                  texts.forEach(t => { if (t.length > 1 && t.length < 80 && !t.includes('Editar')) skillsSet.add(t); });
                }
              });
              if (skillsSet.size === 0) {
                const lines = document.body.innerText.split('\\n');
                const skip = ['Editar','competência','LinkedIn','Exibido','Anúncio','Quem seus visitantes','Sobre','Acessibilidade','Carreiras','Notificações','Mensagens','Vagas','Minha rede','Início','Todos','Conhecimento','Ferramentas','Competências','Recursos','Reative','Premium'];
                lines.forEach(line => {
                  const t = line.trim();
                  if (t.length < 2 || t.length > 80) return;
                  if (/^\\d/.test(t)) return;
                  if (skip.some(w => t.includes(w))) return;
                  if (/[A-ZÀ-Ú]/.test(t) || /\\s/.test(t) || t.length >= 4) skillsSet.add(t);
                });
              }
              data.skills = [...skillsSet].slice(0, 50);
              log('Skills: ' + data.skills.length + ' encontradas');

              // Show result
              const jsonStr = JSON.stringify(data, null, 2);
              const logEl = document.getElementById('li-log');
              if (logEl) {
                logEl.innerHTML = '<div style="margin-bottom:12px;color:#22c55e;font-weight:bold;">✅ Extração completa! Clique em COPIAR abaixo.</div><pre style="background:#0f172a;border:1px solid #334155;border-radius:8px;padding:12px;font-size:11px;color:#94a3b8;max-height:200px;overflow-y:auto;white-space:pre-wrap;">' + jsonStr.replace(/</g,'&lt;') + '</pre><div style="margin-top:12px;display:flex;gap:8px;"><button id="li-copy-btn" style="flex:1;background:#3b82f6;color:white;border:none;border-radius:8px;padding:10px;font-weight:bold;cursor:pointer;font-size:14px;">📋 Copiar JSON</button><button id="li-close-btn" style="background:#334155;color:#94a3b8;border:none;border-radius:8px;padding:10px;cursor:pointer;font-size:14px;">Fechar</button></div>';

                document.getElementById('li-copy-btn').onclick = () => {
                  navigator.clipboard.writeText(jsonStr).then(() => {
                    document.getElementById('li-copy-btn').textContent = '✅ Copiado!';
                    document.getElementById('li-copy-btn').style.background = '#22c55e';
                  });
                };
                document.getElementById('li-close-btn').onclick = () => overlay.remove();
              }
            }, 1000);
          }, 1000);
        }, 2000);
      } else {
        data.skills = [];
        log('Skills: link não encontrado');
        const jsonStr = JSON.stringify(data, null, 2);
        const logEl = document.getElementById('li-log');
        if (logEl) {
          logEl.innerHTML = '<div style="color:#eab308;">⚠ Skills não extraídas. Tente ir manualmente para /details/skills/ e rodar novamente.</div><pre style="background:#0f172a;border:1px solid #334155;border-radius:8px;padding:12px;font-size:11px;color:#94a3b8;max-height:200px;overflow-y:auto;">' + jsonStr.replace(/</g,'&lt;') + '</pre><div style="margin-top:12px;display:flex;gap:8px;"><button id="li-copy-btn" style="flex:1;background:#3b82f6;color:white;border:none;border-radius:8px;padding:10px;font-weight:bold;cursor:pointer;font-size:14px;">📋 Copiar JSON</button><button id="li-close-btn" style="background:#334155;color:#94a3b8;border:none;border-radius:8px;padding:10px;cursor:pointer;font-size:14px;">Fechar</button></div>';
          document.getElementById('li-copy-btn').onclick = () => { navigator.clipboard.writeText(jsonStr).then(() => { document.getElementById('li-copy-btn').textContent = '✅ Copiado!'; document.getElementById('li-copy-btn').style.background = '#22c55e'; }); };
          document.getElementById('li-close-btn').onclick = () => overlay.remove();
        }
      }
    }, 1500);
  }, 500);
})();
`;

export const LinkedInAuditPage = () => {
  const [mode, setMode] = useState<InputMode>('extractor');
  const [profileUrl, setProfileUrl] = useState('');
  const [headline, setHeadline] = useState('');
  const [about, setAbout] = useState('');
  const [experience, setExperience] = useState('');
  const [skills, setSkills] = useState('');
  const [jsonInput, setJsonInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AuditResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [jsonCopied, setJsonCopied] = useState(false);
  const [extractorOpen, setExtractorOpen] = useState(false);
  const [jsonCollapsed, setJsonCollapsed] = useState(false);
  const jsonRef = useRef<HTMLTextAreaElement>(null);

  const fillFromJson = () => {
    try {
      const data = JSON.parse(jsonInput);
      if (data.headline) setHeadline(data.headline);
      if (data.about) setAbout(data.about);
      if (data.experience) setExperience(data.experience);
      if (data.skills && Array.isArray(data.skills)) setSkills(data.skills.join(', '));
      setMode('manual');
      setJsonCopied(false);
    } catch {
      // ignore parse errors, user can still paste manually
    }
  };

  useEffect(() => {
    if (jsonInput.trim()) {
      try {
        const parsed = JSON.parse(jsonInput);
        if (parsed.headline || parsed.about || parsed.experience) {
          fillFromJson();
        }
      } catch { /* not valid JSON yet */ }
    }
  }, [jsonInput]);

  const handleAudit = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('jarvis_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const body = {
        headline,
        about,
        experience,
        skills: skills.split(',').map(s => s.trim()).filter(Boolean),
        target_keywords: [],
      };

      const response = await fetch(`${API_BASE}/linkedin/audit/raw`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Erro na auditoria');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExtractor = () => {
    const url = profileUrl.trim() || 'https://www.linkedin.com/in/silvano-moraes-de-souza/';
    window.open(url, '_blank');
    setExtractorOpen(true);
    setJsonCopied(false);
  };

  const copyExtractorScript = () => {
    navigator.clipboard.writeText(EXTRACTOR_SCRIPT.trim());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const canAudit = !!(headline || about || experience || skills);

  const scoreColor = (s: number) => s >= 70 ? 'text-green-400' : s >= 40 ? 'text-yellow-400' : 'text-red-400';

  const sectionLabels: Record<string, string> = {
    headline: 'Headline',
    about: 'Sobre',
    experience: 'Experiência',
    skills: 'Skills',
    seo: 'SEO',
    authority: 'Autoridade',
  };

  return (
    <section className="pt-28 pb-20 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <h1 className="text-3xl font-black text-white tracking-tight mb-2 flex items-center gap-3">
            <Linkedin size={28} className="text-blue-400" /> Auditoria LinkedIn
          </h1>
          <p className="text-slate-400 text-sm">Extraia dados do seu perfil logado e a IA analisa tudo</p>
        </div>

        {/* Mode Toggle */}
        <div className="flex gap-2 mb-8">
          <button
            onClick={() => { setMode('extractor'); setExtractorOpen(false); }}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
              mode === 'extractor'
                ? 'premium-gradient text-white shadow-lg shadow-blue-500/20'
                : 'glass-panel text-slate-400 hover:text-white'
            }`}
          >
            <Terminal size={16} /> Extrair do Browser
          </button>
          <button
            onClick={() => { setMode('manual'); setExtractorOpen(false); }}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
              mode === 'manual'
                ? 'premium-gradient text-white shadow-lg shadow-blue-500/20'
                : 'glass-panel text-slate-400 hover:text-white'
            }`}
          >
            <FileText size={16} /> Inserir Manualmente
          </button>
        </div>

        {/* EXTRACTOR MODE */}
        {mode === 'extractor' && (
          <div className="space-y-6">
            {/* Step 1: Profile URL */}
            <div className="glass-panel rounded-3xl p-8">
              <div className="flex items-start gap-4">
                <div className="shrink-0 w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-black text-sm">1</div>
                <div className="flex-1">
                  <div className="section-label flex items-center gap-2">
                    <Link2 size={14} className="text-blue-400" /> URL do Perfil LinkedIn
                  </div>
                  <input
                    value={profileUrl}
                    onChange={e => setProfileUrl(e.target.value)}
                    placeholder="https://www.linkedin.com/in/seu-perfil/"
                    className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-5 py-4 text-sm text-white focus:border-blue-500 outline-none transition-all placeholder:text-slate-600"
                    onKeyDown={e => e.key === 'Enter' && handleExtractor()}
                  />
                  <p className="text-xs text-slate-600 mt-3">
                    Cole o link do seu perfil. O sistema vai abrir no seu browser (onde você já está logado).
                  </p>
                </div>
              </div>
            </div>

            {/* Step 2: Run Extractor Script */}
            <div className="glass-panel rounded-3xl p-8">
              <div className="flex items-start gap-4">
                <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-black text-sm">2</div>
                <div className="flex-1">
                  <div className="section-label flex items-center gap-2">
                    <Terminal size={14} className="text-indigo-400" /> Executar Script de Extração
                  </div>

                  {!extractorOpen ? (
                    <button
                      onClick={handleExtractor}
                      disabled={!profileUrl.trim()}
                      className="btn-premium premium-gradient text-white px-8 py-3 rounded-xl text-sm disabled:opacity-40"
                    >
                      <ExternalLink size={16} /> Abrir Perfil + Extrair
                    </button>
                  ) : (
                    <div className="space-y-4">
                      <div className="bg-slate-950/50 border border-slate-800 rounded-xl p-4">
                        <p className="text-sm text-slate-300 mb-3">
                          ✅ Seu perfil abriu em outra aba. Agora:
                        </p>
                        <ol className="text-sm text-slate-400 space-y-2 list-decimal list-inside">
                          <li>Na aba do LinkedIn, pressione <kbd className="px-2 py-0.5 bg-slate-800 rounded text-xs text-white">F12</kbd> (Console)</li>
                          <li>Cole o script abaixo e pressione <kbd className="px-2 py-0.5 bg-slate-800 rounded text-xs text-white">Enter</kbd></li>
                          <li>O script vai extrair tudo automaticamente e mostrar um botão <strong className="text-blue-400">Copiar JSON</strong></li>
                        </ol>
                      </div>

                      <div className="relative">
                        {!jsonCollapsed && (
                          <pre className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-400 max-h-48 overflow-auto whitespace-pre-wrap font-mono">
                            {EXTRACTOR_SCRIPT.trim()}
                          </pre>
                        )}
                        <div className="flex gap-2 mt-3">
                          <button
                            onClick={copyExtractorScript}
                            className="btn-premium premium-gradient text-white px-6 py-2.5 rounded-xl text-sm"
                          >
                            {copied ? <><Check size={14} /> Copiado!</> : <><Copy size={14} /> Copiar Script</>}
                          </button>
                          <button
                            onClick={() => setJsonCollapsed(!jsonCollapsed)}
                            className="glass-panel px-4 py-2.5 rounded-xl text-sm text-slate-400 hover:text-white"
                          >
                            {jsonCollapsed ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Step 3: Paste JSON Result */}
            {extractorOpen && (
              <div className="glass-panel rounded-3xl p-8">
                <div className="flex items-start gap-4">
                  <div className="shrink-0 w-8 h-8 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center font-black text-sm">3</div>
                  <div className="flex-1">
                    <div className="section-label flex items-center gap-2">
                      <Sparkles size={14} className="text-purple-400" /> Colar Dados Extraídos
                    </div>
                    <textarea
                      ref={jsonRef}
                      value={jsonInput}
                      onChange={e => { setJsonInput(e.target.value); setJsonCopied(false); }}
                      placeholder='Cole aqui o JSON extraído: {"headline": "...", "about": "...", ...}'
                      className="w-full h-32 bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white font-mono resize-none focus:border-blue-500 outline-none transition-all placeholder:text-slate-600"
                    />
                    {jsonInput.trim() && (
                      <div className="flex items-center gap-3 mt-3">
                        <span className="text-xs text-green-400 flex items-center gap-1">
                          <Check size={12} /> Dados detectados
                        </span>
                        <button
                          onClick={() => { fillFromJson(); setMode('manual'); }}
                          className="text-xs text-blue-400 hover:text-blue-300 underline"
                        >
                          Preencher formulário automaticamente →
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* MANUAL MODE */}
        {mode === 'manual' && (
          <>
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="card-premium">
                <div className="section-label">Headline</div>
                <input
                  value={headline}
                  onChange={e => setHeadline(e.target.value)}
                  placeholder="Sua headline atual do LinkedIn..."
                  className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all placeholder:text-slate-600"
                />
              </div>
              <div className="card-premium">
                <div className="section-label">Skills (separadas por vírgula)</div>
                <input
                  value={skills}
                  onChange={e => setSkills(e.target.value)}
                  placeholder="Python, SQL, Power BI, Data Analysis..."
                  className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:border-blue-500 outline-none transition-all placeholder:text-slate-600"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="card-premium">
                <div className="section-label">Seção Sobre</div>
                <textarea
                  value={about}
                  onChange={e => setAbout(e.target.value)}
                  placeholder="Cole aqui o texto da seção 'Sobre' do seu LinkedIn..."
                  className="w-full h-40 bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white resize-none focus:border-blue-500 outline-none transition-all placeholder:text-slate-600"
                />
              </div>
              <div className="card-premium">
                <div className="section-label">Experiência</div>
                <textarea
                  value={experience}
                  onChange={e => setExperience(e.target.value)}
                  placeholder="Cole aqui os bullets das suas experiências no LinkedIn..."
                  className="w-full h-40 bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white resize-none focus:border-blue-500 outline-none transition-all placeholder:text-slate-600"
                />
              </div>
            </div>
          </>
        )}

        {/* Audit Button */}
        <div className="flex justify-center mb-12">
          <button
            onClick={handleAudit}
            disabled={loading || !canAudit}
            className="btn-premium premium-gradient text-white px-10 py-4 rounded-2xl text-lg shadow-xl shadow-blue-500/25 hover:shadow-blue-500/40 disabled:opacity-50"
          >
            {loading ? 'Auditando Perfil...' : <><Sparkles size={20} /> Auditar LinkedIn</>}
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-500/10 text-red-400 rounded-2xl border border-red-500/20 text-center text-sm mb-8 animate-fade-in-up">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="glass-panel rounded-[40px] p-8 text-center">
              <div className="section-label">Score LinkedIn</div>
              <div className={`text-6xl font-black ${scoreColor(result.overall_score)} mb-2`}>
                {result.overall_score}
              </div>
              <span className="text-slate-500 text-sm">de 100 pontos</span>
            </div>

            <div className="glass-panel rounded-[40px] p-8">
              <div className="section-label">Score por Seção</div>
              <div className="grid md:grid-cols-3 gap-4">
                {Object.entries(result.scores).map(([key, value]) => (
                  <div key={key} className="card-flat text-center">
                    <div className={`text-2xl font-black ${scoreColor(value as number)}`}>
                      {value as number}
                    </div>
                    <div className="text-xs text-slate-500 font-bold uppercase">
                      {sectionLabels[key] || key}
                    </div>
                    <div className="progress-bar mt-2">
                      <div
                        className={`progress-bar-fill ${(value as number) >= 70 ? 'bg-green-500' : (value as number) >= 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${value}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {result.quick_wins.length > 0 && (
              <div className="glass-panel rounded-[40px] p-8">
                <div className="section-label flex items-center gap-2">
                  <Lightbulb size={14} className="text-yellow-400" /> Ganhos Rápidos
                </div>
                <div className="space-y-3">
                  {result.quick_wins.map((qw, i) => (
                    <div key={i} className="card-flat p-4 flex items-center gap-4">
                      <span className={`shrink-0 badge-plan ${
                        qw.impact === 'high' ? 'badge-elite' : qw.impact === 'medium' ? 'badge-pro' : 'badge-free'
                      }`}>
                        {qw.impact.toUpperCase()}
                      </span>
                      <span className="text-sm text-slate-300 flex-1">{qw.action}</span>
                      <span className="text-[10px] text-slate-500 uppercase font-bold">{qw.effort}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.issues.length > 0 && (
              <div className="glass-panel rounded-[40px] p-8">
                <div className="section-label flex items-center gap-2">
                  <AlertTriangle size={14} className="text-yellow-400" /> Problemas Encontrados
                </div>
                <div className="space-y-3">
                  {result.issues.map((issue, i) => (
                    <div key={i} className="card-flat p-4">
                      <div className="flex items-start gap-3">
                        <XCircle size={16} className="text-red-400 shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm text-slate-300">{issue.error}</p>
                          {issue.fix && <p className="text-xs text-green-400 mt-1">Correção: {issue.fix}</p>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.ai_audit && Object.keys(result.ai_audit).length > 0 && !result.ai_audit.scrape_failed && (
              <div className="glass-panel rounded-[40px] p-8">
                <div className="section-label flex items-center gap-2">
                  <Sparkles size={14} className="text-blue-400" /> Análise IA
                </div>
                <div className="space-y-4">
                  {result.ai_audit.priority_actions && (
                    <div>
                      <div className="text-xs text-slate-400 font-bold mb-2">Ações Prioritárias</div>
                      {result.ai_audit.priority_actions.map((a: any, i: number) => (
                        <div key={i} className="card-flat p-3 mb-2 flex items-center gap-3">
                          <span className={`shrink-0 badge-plan ${
                            a.impact === 'high' ? 'badge-elite' : a.impact === 'medium' ? 'badge-pro' : 'badge-free'
                          }`}>{a.impact?.toUpperCase()}</span>
                          <span className="text-sm text-slate-300">{a.action}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {result.ai_audit.headline && result.ai_audit.headline.suggested && (
                    <div className="p-6 rounded-3xl bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border border-blue-500/30">
                      <div className="text-xs text-blue-400 font-bold mb-2">Headline Sugerida</div>
                      <p className="text-lg font-black text-white">{result.ai_audit.headline.suggested}</p>
                      {result.ai_audit.headline.why && <p className="text-xs text-slate-500 mt-2">{result.ai_audit.headline.why}</p>}
                    </div>
                  )}
                  {result.ai_audit.about && result.ai_audit.about.suggested && (
                    <div className="card-flat p-4">
                      <div className="text-xs text-blue-400 font-bold mb-2">Seção Sobre Sugerida</div>
                      <p className="text-sm text-slate-300 leading-relaxed">{result.ai_audit.about.suggested}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};
