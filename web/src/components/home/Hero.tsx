// ================================================================
// JARVIS CV
// ARQUIVO: Hero.tsx
// DESCRIÇÃO: Hero premium com conversion copywriting + mini sparkline
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 3.1.0
// ================================================================
import { useState, useEffect, useRef } from 'react';
import { ArrowRight, Sparkles, Shield, Zap, TrendingUp } from 'lucide-react';

function useCountUp(target: number, duration: number = 1800, startOnView: boolean = true) {
  const [value, setValue] = useState(0);
  const [started, setStarted] = useState(!startOnView);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!startOnView) return;
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setStarted(true); observer.disconnect(); } },
      { threshold: 0.3 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [startOnView]);

  useEffect(() => {
    if (!started) return;
    const start = performance.now();
    const step = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [started, target, duration]);

  return { value, ref };
}

function MiniSparkline({ color, dashed }: { color: string; dashed?: boolean }) {
  const points = '5,28 15,22 25,26 35,14 45,18 55,8 65,12 75,4 85,10 95,2';
  return (
    <svg viewBox="0 0 100 32" className="w-full h-8 mt-2" preserveAspectRatio="none">
      {dashed && (
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="1.5"
          strokeDasharray="4 3"
          opacity="0.4"
        />
      )}
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={dashed ? '' : 'opacity-60'}
      />
      <linearGradient id={`grad-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={color} stopOpacity="0.3" />
        <stop offset="100%" stopColor={color} stopOpacity="0" />
      </linearGradient>
      <polygon
        points={`5,32 ${points} 95,32`}
        fill={`url(#grad-${color.replace('#', '')})`}
      />
    </svg>
  );
}

const stats = [
  // Números do próprio produto (ats_weights, job_scraper, ai_engine), não estatísticas de mercado.
  {
    value: 6,
    suffix: '',
    label: 'Dimensões de Score',
    icon: Zap,
    color: '#3b82f6',
    sparkColor: '#3b82f6',
    dashed: false,
  },
  {
    value: 9,
    suffix: '',
    label: 'Portais de Vagas',
    icon: Shield,
    color: '#22c55e',
    sparkColor: '#22c55e',
    dashed: true,
  },
  {
    value: 5,
    suffix: '',
    label: 'Modelos de IA',
    icon: TrendingUp,
    color: '#a855f7',
    sparkColor: '#a855f7',
    dashed: true,
  },
];

export const Hero = () => {
  const scrollToAnalyzer = () => {
    document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' });
  };

  const counters = stats.map(s => useCountUp(s.value, 2000));

  return (
    <section className="relative pt-32 pb-32 px-6 overflow-hidden">
      <div className="glow-effect w-[600px] h-[600px] bg-blue-600 top-[-20%] left-[-10%] opacity-30" />
      <div className="glow-effect w-[600px] h-[600px] bg-indigo-600 bottom-[-20%] right-[-10%] opacity-20" />
      <div className="glow-effect w-[300px] h-[300px] bg-purple-600 top-[30%] right-[10%] opacity-10" />

      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          
          {/* Left: Text Content */}
          <div className="text-left">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold mb-8 animate-fade-in-up">
              <Sparkles size={14} />
              <span>Motor ATS Híbrido - Local + IA</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-black tracking-tighter mb-8 leading-[1.05] text-white animate-fade-in-up delay-100">
              Seu currículo passa<br />
              <span className="premium-gradient-text">no filtro ATS?</span>
            </h1>

            <p className="text-lg md:text-xl text-slate-400 max-w-xl mb-2 leading-relaxed animate-fade-in-up delay-200">
              Uma nota de 0 a 100 em 6 dimensões mostra onde seu currículo perde pontos para a vaga.</p>
            <p className="text-lg md:text-xl text-slate-400 max-w-xl mb-10 leading-relaxed animate-fade-in-up delay-200">
              A IA reescreve o que falta, e você busca vagas em 9 portais de uma vez.
            </p>

            <div className="flex flex-col sm:flex-row items-start gap-4 mb-12 animate-fade-in-up delay-300">
              <button
                onClick={scrollToAnalyzer}
                className="btn-premium premium-gradient text-white px-10 py-4 rounded-2xl text-lg shadow-xl shadow-blue-500/25 hover:shadow-blue-500/40 group"
              >
                Analisar Agora é Grátis
                <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={scrollToAnalyzer}
                className="btn-ghost px-10 py-4 rounded-2xl text-lg"
              >
                Ver Demo
              </button>
            </div>

            {/* Mini stat cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-xl animate-fade-in-up delay-400">
              {stats.map((stat, i) => {
                const Icon = stat.icon;
                const counter = counters[i];
                return (
                  <div
                    key={stat.label}
                    ref={counter.ref}
                    className="glass-panel rounded-2xl p-4 text-center group hover:border-blue-500/40 transition-all duration-500 hover:-translate-y-1"
                  >
                    <div className="flex items-center justify-center gap-2 mb-1">
                      <Icon size={16} style={{ color: stat.color }} />
                      <span className="text-white font-black text-2xl tabular-nums">
                        {counter.value}{stat.suffix}
                      </span>
                    </div>
                    <span className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">
                      {stat.label}
                    </span>
                    <MiniSparkline color={stat.sparkColor} dashed={stat.dashed} />
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: ATS Filter Illustration */}
          <div className="relative hidden lg:flex items-center justify-center animate-fade-in-up delay-200">
            <div className="relative w-full max-w-lg">
              {/* Background glow */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-indigo-600/10 to-purple-600/20 rounded-3xl blur-3xl" />
              
              <svg viewBox="0 0 500 500" className="relative w-full h-auto" fill="none" xmlns="http://www.w3.org/2000/svg">
                {/* Scanner frame */}
                <rect x="120" y="80" width="260" height="340" rx="16" fill="#0f172a" stroke="#1e293b" strokeWidth="2" />
                <rect x="120" y="80" width="260" height="340" rx="16" stroke="url(#scanGrad)" strokeWidth="1" opacity="0.5" />
                
                {/* Scanner header */}
                <rect x="120" y="80" width="260" height="44" rx="16" fill="#1e293b" />
                <rect x="120" y="108" width="260" height="16" fill="#1e293b" />
                <circle cx="145" cy="102" r="5" fill="#ef4444" opacity="0.8" />
                <circle cx="162" cy="102" r="5" fill="#eab308" opacity="0.8" />
                <circle cx="179" cy="102" r="5" fill="#22c55e" opacity="0.8" />
                <text x="250" y="107" textAnchor="middle" fill="#94a3b8" fontSize="11" fontWeight="700" fontFamily="system-ui">JARVIS ATS ENGINE</text>
                
                {/* Scanning line */}
                <rect x="130" y="180" width="240" height="2" fill="url(#scanLine)" opacity="0.8">
                  <animate attributeName="y" values="130;380;130" dur="4s" repeatCount="indefinite" />
                </rect>
                <rect x="130" y="178" width="240" height="6" fill="url(#scanGlow)" opacity="0.3">
                  <animate attributeName="y" values="128;378;128" dur="4s" repeatCount="indefinite" />
                </rect>
                
                {/* Document being scanned */}
                <rect x="150" y="135" width="200" height="260" rx="8" fill="#1e293b" stroke="#334155" strokeWidth="1" />
                
                {/* Document lines */}
                <rect x="165" y="155" width="120" height="8" rx="4" fill="#475569" />
                <rect x="165" y="175" width="170" height="6" rx="3" fill="#334155" />
                <rect x="165" y="189" width="155" height="6" rx="3" fill="#334155" />
                <rect x="165" y="203" width="140" height="6" rx="3" fill="#334155" />
                <rect x="165" y="217" width="160" height="6" rx="3" fill="#334155" />
                
                {/* Skills section */}
                <rect x="165" y="240" width="80" height="6" rx="3" fill="#475569" />
                <rect x="165" y="254" width="50" height="18" rx="9" fill="#3b82f6" opacity="0.2" stroke="#3b82f6" strokeWidth="0.5" />
                <text x="190" y="267" textAnchor="middle" fill="#60a5fa" fontSize="8" fontFamily="system-ui">Python</text>
                <rect x="220" y="254" width="45" height="18" rx="9" fill="#3b82f6" opacity="0.2" stroke="#3b82f6" strokeWidth="0.5" />
                <text x="242" y="267" textAnchor="middle" fill="#60a5fa" fontSize="8" fontFamily="system-ui">SQL</text>
                <rect x="270" y="254" width="55" height="18" rx="9" fill="#8b5cf6" opacity="0.2" stroke="#8b5cf6" strokeWidth="0.5" />
                <text x="297" y="267" textAnchor="middle" fill="#a78bfa" fontSize="8" fontFamily="system-ui">Power BI</text>
                
                {/* More document lines */}
                <rect x="165" y="285" width="145" height="6" rx="3" fill="#334155" />
                <rect x="165" y="299" width="130" height="6" rx="3" fill="#334155" />
                <rect x="165" y="313" width="150" height="6" rx="3" fill="#334155" />
                <rect x="165" y="327" width="110" height="6" rx="3" fill="#334155" />
                
                {/* Score badge */}
                <rect x="155" y="350" width="190" height="32" rx="8" fill="#0f172a" stroke="#334155" strokeWidth="1" />
                <text x="175" y="371" fill="#64748b" fontSize="10" fontFamily="system-ui">ATS Score:</text>
                <text x="240" y="371" textAnchor="middle" fill="#22c55e" fontSize="14" fontWeight="800" fontFamily="system-ui">
                  92
                  <animate attributeName="opacity" values="1;0.6;1" dur="2s" repeatCount="indefinite" />
                </text>
                <text x="330" y="371" fill="#64748b" fontSize="10" fontFamily="system-ui">/100</text>
                <rect x="265" y="358" width="60" height="4" rx="2" fill="#1e293b" />
                <rect x="265" y="358" width="55" height="4" rx="2" fill="#22c55e">
                  <animate attributeName="width" values="0;55" dur="2s" fill="freeze" />
                </rect>
                
                {/* Incoming documents (left side) */}
                <g opacity="0.6">
                  <rect x="30" y="150" width="70" height="90" rx="6" fill="#1e293b" stroke="#334155" strokeWidth="1" transform="rotate(-15, 65, 195)" />
                  <rect x="38" y="165" width="50" height="4" rx="2" fill="#475569" transform="rotate(-15, 65, 195)" />
                  <rect x="38" y="175" width="40" height="4" rx="2" fill="#475569" transform="rotate(-15, 65, 195)" />
                  <rect x="38" y="185" width="45" height="4" rx="2" fill="#475569" transform="rotate(-15, 65, 195)" />
                  <rect x="45" y="205" width="35" height="14" rx="7" fill="#ef4444" opacity="0.3" transform="rotate(-15, 65, 195)" />
                  <text x="63" y="216" textAnchor="middle" fill="#f87171" fontSize="7" transform="rotate(-15, 65, 195)">REJEITADO</text>
                </g>
                
                <g opacity="0.4">
                  <rect x="25" y="260" width="70" height="90" rx="6" fill="#1e293b" stroke="#334155" strokeWidth="1" transform="rotate(-10, 60, 305)" />
                  <rect x="33" y="275" width="50" height="4" rx="2" fill="#475569" transform="rotate(-10, 60, 305)" />
                  <rect x="33" y="285" width="40" height="4" rx="2" fill="#475569" transform="rotate(-10, 60, 305)" />
                  <rect x="40" y="310" width="35" height="14" rx="7" fill="#ef4444" opacity="0.3" transform="rotate(-10, 60, 305)" />
                  <text x="58" y="321" textAnchor="middle" fill="#f87171" fontSize="7" transform="rotate(-10, 60, 305)">REJEITADO</text>
                </g>
                
                {/* Approved document (right side) */}
                <g opacity="0.8">
                  <rect x="400" y="180" width="70" height="90" rx="6" fill="#1e293b" stroke="#22c55e" strokeWidth="1" transform="rotate(10, 435, 225)" />
                  <rect x="408" y="195" width="50" height="4" rx="2" fill="#475569" transform="rotate(10, 435, 225)" />
                  <rect x="408" y="205" width="40" height="4" rx="2" fill="#475569" transform="rotate(10, 435, 225)" />
                  <rect x="415" y="230" width="35" height="14" rx="7" fill="#22c55e" opacity="0.3" transform="rotate(10, 435, 225)" />
                  <text x="433" y="241" textAnchor="middle" fill="#4ade80" fontSize="7" transform="rotate(10, 435, 225)">APROVADO</text>
                </g>
                
                {/* Arrow flow indicators */}
                <path d="M100 200 L120 200" stroke="#475569" strokeWidth="2" strokeDasharray="4 2" markerEnd="url(#arrowGray)" />
                <path d="M380 220 L400 220" stroke="#22c55e" strokeWidth="2" strokeDasharray="4 2" markerEnd="url(#arrowGreen)" />
                
                {/* Floating particles */}
                <circle cx="100" cy="120" r="3" fill="#3b82f6" opacity="0.4">
                  <animate attributeName="cy" values="120;100;120" dur="3s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.4;0.1;0.4" dur="3s" repeatCount="indefinite" />
                </circle>
                <circle cx="420" cy="150" r="2" fill="#8b5cf6" opacity="0.3">
                  <animate attributeName="cy" values="150;130;150" dur="4s" repeatCount="indefinite" />
                </circle>
                <circle cx="80" cy="300" r="2" fill="#3b82f6" opacity="0.2">
                  <animate attributeName="cy" values="300;280;300" dur="3.5s" repeatCount="indefinite" />
                </circle>
                <circle cx="440" cy="320" r="3" fill="#22c55e" opacity="0.3">
                  <animate attributeName="cy" values="320;300;320" dur="2.5s" repeatCount="indefinite" />
                </circle>
                
                {/* Connection nodes */}
                <circle cx="100" cy="200" r="4" fill="#3b82f6" opacity="0.6">
                  <animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle cx="400" cy="220" r="4" fill="#22c55e" opacity="0.6">
                  <animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite" />
                </circle>
                
                <defs>
                  <linearGradient id="scanGrad" x1="120" y1="80" x2="380" y2="420">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="50%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#a855f7" />
                  </linearGradient>
                  <linearGradient id="scanLine" x1="130" y1="0" x2="370" y2="0">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
                    <stop offset="50%" stopColor="#3b82f6" stopOpacity="1" />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                  </linearGradient>
                  <linearGradient id="scanGlow" x1="130" y1="0" x2="370" y2="0">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
                    <stop offset="50%" stopColor="#60a5fa" stopOpacity="1" />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                  </linearGradient>
                  <marker id="arrowGray" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
                    <path d="M0,0 L6,2 L0,4" fill="#475569" />
                  </marker>
                  <marker id="arrowGreen" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
                    <path d="M0,0 L6,2 L0,4" fill="#22c55e" />
                  </marker>
                </defs>
              </svg>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};