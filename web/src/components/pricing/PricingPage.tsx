// ================================================================
// JARVIS CV
// ARQUIVO: PricingPage.tsx
// DESCRIÇÃO: Página de preços com cards de planos (Free, Pro, Elite)
// AUTOR: SILVANO MORAES DE SOUZA
// VERSÃO: 2.0.0
// ================================================================
import { Check, Zap, Crown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../../config';

const plans = [
  {
    id: 'free',
    name: 'Gratuito',
    price: 'R$ 0',
    period: '/mês',
    icon: <Zap size={24} className="text-slate-400" />,
    features: [
      'Análise ATS básica',
      '3 análises por dia',
      '3 vagas por dia',
      'Upload de currículo',
    ],
    cta: 'Começar Grátis',
    highlight: false,
    gradient: '',
  },
  {
    id: 'pro',
    name: 'Profissional',
    price: 'R$ 49',
    period: '/mês',
    icon: <Check size={24} className="text-blue-400" />,
    features: [
      'Tudo do Gratuito',
      '15 análises por dia',
      '15 vagas por dia',
      'Download DOCX otimizado',
      'Reescrita de currículo por IA',
      'Suporte prioritário',
    ],
    cta: 'Assinar Pro',
    highlight: true,
    gradient: 'premium-gradient',
  },
  {
    id: 'elite',
    name: 'Elite',
    price: 'R$ 149',
    period: '/mês',
    icon: <Crown size={24} className="text-purple-400" />,
    features: [
      'Tudo do Profissional',
      'Análises ilimitadas',
      'Vagas ilimitadas',
      'Carta de apresentação por IA',
      'Estratégia semanal personalizada',
      'Auto-apply (em breve)',
      'Suporte VIP',
    ],
    cta: 'Assinar Elite',
    highlight: false,
    gradient: '',
  },
];

export const PricingPage = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('jarvis_token');

  const handleSubscribe = async (planId: string) => {
    if (planId === 'free') {
      navigate('/registro');
      return;
    }

    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/payments/checkout?plan=${planId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Erro ao criar checkout.');

      const data = await response.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (err) {
      console.error('Erro no checkout:', err);
    }
  };

  return (
    <section className="min-h-[80vh] pt-32 pb-20 px-6">
      <div className="max-w-5xl mx-auto text-center mb-16">
        <h2 className="text-5xl font-black text-white tracking-tight mb-4">
          Escolha seu <span className="text-transparent bg-clip-text premium-gradient">plano de poder</span>
        </h2>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Desbloqueie o potencial completo da IA para transformar sua carreira.
        </p>
      </div>

      <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`glass-panel rounded-3xl p-8 border transition-all hover:-translate-y-2 ${
              plan.highlight
                ? 'border-blue-500/50 shadow-xl shadow-blue-500/20 scale-[1.02]'
                : 'border-slate-800/60'
            }`}
          >
            <div className="flex items-center gap-3 mb-6">
              {plan.icon}
              <h3 className="text-xl font-bold text-white">{plan.name}</h3>
            </div>

            <div className="mb-8">
              <span className="text-4xl font-black text-white">{plan.price}</span>
              <span className="text-slate-500 text-sm">{plan.period}</span>
            </div>

            <ul className="space-y-4 mb-8">
              {plan.features.map((feature, i) => (
                <li key={i} className="flex items-start gap-3 text-slate-300 text-sm">
                  <span className="text-blue-500 font-bold mt-0.5">✓</span>
                  {feature}
                </li>
              ))}
            </ul>

            <button
              onClick={() => handleSubscribe(plan.id)}
              className={`w-full py-3.5 rounded-xl font-bold text-sm transition-all hover:scale-[1.02] active:scale-95 ${
                plan.highlight
                  ? 'premium-gradient text-white shadow-lg shadow-blue-500/20'
                  : 'bg-slate-800 text-white hover:bg-slate-700'
              }`}
            >
              {plan.cta}
            </button>
          </div>
        ))}
      </div>
    </section>
  );
};
