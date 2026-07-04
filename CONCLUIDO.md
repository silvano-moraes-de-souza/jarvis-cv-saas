# ================================================================
# JARVIS CV
# ARQUIVO: CONCLUIDO.md
# DESCRIÇÃO: Relatório completo de progresso e documentação arquitetural
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================

# JARVIS CV — Plataforma SaaS de Otimização de Carreira com IA

---

## HISTÓRICO DE FASES ANTERIORES (v1.x)

### Fase 1: Arquitetura Inicial
- Montagem do banco de dados no Supabase com tabelas de perfis, currículos, LinkedIn e vagas.
- Definição de comunicação com IA via Edge Functions.
- Organização de pastas (Web, Supabase, Core).
- Implementação de RLS para isolamento de dados.

### Fase 2: Interface Premium
- Design system estilo Stripe/Linear com Dark Mode.
- Componentes de alta conversão (Navbar Blur, Hero Section).
- Dashboard de Match com visual de análise de elite.
- Glassmorphism e tipografia de alta performance.

### Fase 3: Backend e Integração de IA
- Edge Functions para comunicação com API.
- Lógica de ATS Score, skills faltantes e melhorias.
- Reescrita automática de resumo profissional.

### Fase 4-7: Refinamentos
- UX High-End com animações e micro-interações.
- Backend Node.js com Express.
- Persona de Especialista Global em Recrutamento.
- Fluxo E2E: Input → Servidor → IA → Interface.
- Migração de Groq para NVIDIA API (Qwen 3.5 122B).
- Tradução completa para pt-BR.
- Sistema de logs de execução.

---

## FASE 8: ARQUITETURA SaaS COMPLETA (v2.0)

**Data: 02/05/2026**
**Status: Em andamento**

---

### 1. ARQUITETURA TÉCNICA COMPLETA

```
┌─────────────────────────────────────────────────────────┐
│                    JARVIS CV SaaS v2.0                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   FRONTEND   │    │   BACKEND   │    │   WORKERS   │ │
│  │  React+TW    │───▶│  FastAPI    │───▶│  Redis Queue│ │
│  │  Framer Mot. │    │  Python     │    │  Celery     │ │
│  │  Supabase    │◀───│  JWT Auth   │    │  Scraper    │ │
│  └─────────────┘    └──────┬──────┘    └─────────────┘ │
│                            │                            │
│         ┌──────────────────┼──────────────────┐         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   SUPABASE   │  │   NVIDIA    │  │   REDIS     │   │
│  │   PostgreSQL │  │   API       │  │   Cache     │   │
│  │   Auth       │  │   Multi-LLM │  │   Sessions  │   │
│  │   Storage    │  │   (Qwen 3.5)│  │   Rate Lim. │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   STRIPE     │  │  DOCX GEN   │  │  SCRAPER    │   │
│  │   Payments   │  │  python-docx│  │  Modular    │   │
│  │   Webhooks   │  │  Templates  │  │  Ético      │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Stack Técnica Definitiva

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Frontend | React 18 + Tailwind + Framer Motion | UX premium, animações fluidas, mobile-first |
| Backend | FastAPI (Python) | Async nativo, tipagem forte, OpenAPI automático |
| Banco | Supabase (PostgreSQL) | Auth integrado, RLS, Storage, Realtime |
| Cache/Fila | Redis + Celery | Rate limiting, filas de análise, sessões |
| IA | NVIDIA API (Qwen 3.5 122B) | Já integrada, resposta rápida, custo baixo |
| Pagamentos | Stripe | SaaS standard, webhooks, assinaturas |
| Documentos | python-docx | Geração DOCX premium com templates |
| Scraping | Playwright + BeautifulSoup | Scraping ético modular de vagas |
| Deploy | Vercel (FE) + Railway (BE) | CI/CD, scaling automático |

#### Estrutura de Pastas (v2.0)

```
JARVIS CV/
├── web/                          # Frontend React
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/           # Navbar, Footer, Sidebar
│   │   │   ├── home/             # Hero, Features, Pricing
│   │   │   ├── auth/             # Login, Register, ForgotPassword
│   │   │   ├── dashboard/        # Dashboard principal
│   │   │   ├── analysis/         # Upload, MatchResult, ScoreCard
│   │   │   ├── jobs/             # JobList, JobCard, JobSearch
│   │   │   ├── documents/        # DOCXPreview, ExportButton
│   │   │   └── pricing/          # PlanCard, Checkout
│   │   ├── hooks/                # useAuth, useAnalysis, useJobs
│   │   ├── services/             # api.ts, supabase.ts
│   │   ├── contexts/             # AuthContext, ThemeContext
│   │   ├── pages/                # Home, Dashboard, Analysis, Jobs, Pricing
│   │   └── utils/                # formatters, validators
│   └── package.json
│
├── api/                          # Backend FastAPI (NOVO - substitui backend/)
│   ├── app/
│   │   ├── main.py               # Entry point FastAPI
│   │   ├── config.py             # Settings, env vars
│   │   ├── dependencies.py       # Auth, rate limiting, plan checking
│   │   ├── models/               # SQLAlchemy/Pydantic models
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   └── analysis.py
│   │   ├── routers/              # Endpoints organizados por domínio
│   │   │   ├── auth.py           # Login, register, refresh
│   │   │   ├── resumes.py        # Upload, CRUD de currículos
│   │   │   ├── analysis.py       # Análise ATS com IA
│   │   │   ├── jobs.py           # Busca e CRUD de vagas
│   │   │   ├── documents.py      # Geração DOCX
│   │   │   ├── payments.py       # Stripe webhooks e checkout
│   │   │   └── health.py         # Health check
│   │   ├── services/             # Lógica de negócio
│   │   │   ├── ai_engine.py      # NVIDIA API multi-model
│   │   │   ├── ats_analyzer.py   # Algoritmos de scoring ATS
│   │   │   ├── docx_generator.py # Geração de documentos Word
│   │   │   ├── job_scraper.py    # Scraping ético modular
│   │   │   ├── resume_parser.py  # Parse de PDF/DOCX/TXT
│   │   │   └── stripe_service.py # Lógica de pagamentos
│   │   ├── workers/              # Tarefas assíncronas
│   │   │   ├── celery_app.py     # Configuração Celery
│   │   │   ├── analysis_worker.py # Worker de análise IA
│   │   │   ├── scrape_worker.py  # Worker de scraping
│   │   │   └── docx_worker.py    # Worker de geração DOCX
│   │   └── utils/                # Helpers, validators, logger
│   │       ├── logger.py
│   │       ├── rate_limiter.py
│   │       └── lgpd.py           # Utilidades LGPD
│   ├── requirements.txt
│   └── Dockerfile
│
├── supabase/
│   ├── functions/                 # Edge Functions (Deno)
│   │   ├── analyze-raw/
│   │   └── analyze-match/
│   └── migrations/                # SQL migrations
│       ├── 001_init_saas_architecture.sql
│       ├── 002_saas_plans_subscriptions.sql
│       └── 003_update_optimization_results.sql
│
├── CONCLUIDO.md                   # Este arquivo
└── README.md                      # Documentação técnica
```

---

### 2. BANCO DE DADOS COMPLETO (Supabase PostgreSQL)

#### Tabela: `profiles`
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  auth_id UUID UNIQUE NOT NULL REFERENCES auth.users(id),
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  phone TEXT,
  current_role TEXT,
  linkedin_url TEXT,
  avatar_url TEXT,
  plan TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'elite')),
  daily_analyses_used INTEGER DEFAULT 0,
  daily_jobs_used INTEGER DEFAULT 0,
  usage_reset_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Tabela: `subscriptions`
```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  stripe_customer_id TEXT UNIQUE,
  stripe_subscription_id TEXT UNIQUE,
  plan TEXT NOT NULL CHECK (plan IN ('free', 'pro', 'elite')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'past_due', 'canceled', 'trialing')),
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at_period_end BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Tabela: `resumes`
```sql
CREATE TABLE resumes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL DEFAULT 'Meu Currículo',
  file_url TEXT,                    -- URL do arquivo no Supabase Storage
  file_type TEXT CHECK (file_type IN ('pdf', 'docx', 'txt')),
  raw_text TEXT,                    -- Texto extraído para processamento IA
  content JSONB,                    -- Estrutura parseada (seções, experiência, etc.)
  version_number INTEGER NOT NULL DEFAULT 1,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_user_version UNIQUE (user_id, version_number)
);
```

#### Tabela: `target_jobs`
```sql
CREATE TABLE target_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  company TEXT,
  description TEXT NOT NULL,
  url TEXT,
  source TEXT CHECK (source IN ('manual', 'linkedin', 'indeed', 'glassdoor', 'gulf_talent', 'bayt', 'other')),
  location TEXT,
  salary_range TEXT,
  is_remote BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Tabela: `optimization_results`
```sql
CREATE TABLE optimization_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  resume_id UUID REFERENCES resumes(id),
  job_id UUID REFERENCES target_jobs(id),
  ats_score DECIMAL(5,2),
  strengths JSONB DEFAULT '[]',
  weaknesses JSONB DEFAULT '[]',
  missing_skills JSONB DEFAULT '[]',
  rewritten_summary TEXT,
  suggested_headline TEXT,
  recommendations JSONB DEFAULT '[]',
  cover_letter TEXT,               -- Carta de apresentação gerada (ELITE)
  optimized_resume_url TEXT,        -- URL do DOCX otimizado (PRO/ELITE)
  analysis_meta JSONB,             -- Metadados da análise (modelo IA, tempo, etc.)
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Tabela: `linkedin_snapshots`
```sql
CREATE TABLE linkedin_snapshots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  headline TEXT,
  about TEXT,
  experience JSONB,
  skills JSONB,
  snapshot_date TIMESTAMPTZ DEFAULT NOW(),
  analysis_score DECIMAL(5,2)
);
```

#### Tabela: `usage_logs` (Auditoria LGPD + Rate Limiting)
```sql
CREATE TABLE usage_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  action TEXT NOT NULL CHECK (action IN ('analysis', 'job_search', 'docx_export', 'cover_letter', 'auto_apply')),
  credits_used INTEGER DEFAULT 1,
  metadata JSONB,
  ip_address INET,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Tabela: `weekly_strategies` (ELITE)
```sql
CREATE TABLE weekly_strategies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  week_start DATE NOT NULL,
  strategy_text TEXT NOT NULL,
  target_jobs JSONB DEFAULT '[]',
  action_items JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Índices para Performance
```sql
CREATE INDEX idx_profiles_auth ON profiles(auth_id);
CREATE INDEX idx_profiles_plan ON profiles(plan);
CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_resumes_user_active ON resumes(user_id, is_active);
CREATE INDEX idx_jobs_user ON target_jobs(user_id);
CREATE INDEX idx_optimization_user ON optimization_results(user_id);
CREATE INDEX idx_optimization_resume_job ON optimization_results(resume_id, job_id);
CREATE INDEX idx_usage_logs_user_date ON usage_logs(user_id, created_at);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);
```

#### RLS (Row Level Security) — LGPD
```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE target_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE optimization_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE linkedin_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_strategies ENABLE ROW LEVEL SECURITY;

-- Cada usuário só acessa seus próprios dados
CREATE POLICY "user_own_profile" ON profiles FOR ALL USING (auth.uid() = auth_id);
CREATE POLICY "user_own_resumes" ON resumes FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = resumes.user_id));
CREATE POLICY "user_own_jobs" ON target_jobs FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = target_jobs.user_id));
CREATE POLICY "user_own_results" ON optimization_results FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = optimization_results.user_id));
CREATE POLICY "user_own_linkedin" ON linkedin_snapshots FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = linkedin_snapshots.user_id));
CREATE POLICY "user_own_subscriptions" ON subscriptions FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = subscriptions.user_id));
CREATE POLICY "user_own_usage" ON usage_logs FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = usage_logs.user_id));
CREATE POLICY "user_own_strategies" ON weekly_strategies FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = weekly_strategies.user_id));
```

---

### 3. FLUXO DE USUÁRIOS

#### Fluxo de Onboarding
```
1. Usuário acessa landing page → Clica "Começar Agora"
2. Cadastro via email/senha ou Google OAuth (Supabase Auth)
3. Trigger automático cria perfil com plan=free
4. Redireciona para Dashboard com tutorial interativo
5. Primeiro upload de currículo é gratuito (hook de conversão)
```

#### Fluxo de Análise ATS
```
1. Usuário faz upload de currículo (PDF/DOCX/TXT)
2. Backend extrai texto via resume_parser.py
3. Usuário cola ou busca descrição da vaga
4. Sistema verifica créditos do plano
5. Se créditos OK → enfileira análise no Celery
6. Worker chama NVIDIA API com prompt especializado
7. IA retorna: score, forças, fraquezas, skills, resumo, headline, recomendações
8. Resultado salvo no Supabase + exibido no Dashboard
9. PRO/ELITE: gera DOCX otimizado automaticamente
10. ELITE: gera carta de apresentação + estratégia semanal
```

#### Fluxo de Busca de Vagas
```
1. Usuário insere cargo desejado + localização
2. Sistema verifica limites do plano (3/15/ilimitado)
3. Worker faz scraping ético dos portais configurados
4. Vagas encontradas são salvas em target_jobs
5. Usuário pode selecionar vaga → iniciar análise ATS
6. ELITE: auto-apply assistido (preenche formulários)
```

#### Fluxo de Pagamento
```
1. Usuário clica em "Upgrade" no Dashboard
2. Redireciona para Stripe Checkout
3. Pagamento processado → Stripe envia webhook
4. Backend atualiza plano no perfil + subscriptions
5. Novos créditos desbloqueados imediatamente
6. Se cancelar → acesso até fim do período pago
```

#### Fluxo de Exportação DOCX (PRO/ELITE)
```
1. Após análise, botão "Baixar Currículo Otimizado" aparece
2. Worker gera DOCX com template premium
3. Resumo reescrito + skills destacados + formatação ATS-friendly
4. Arquivo enviado para Supabase Storage
5. URL temporária gerada para download (expira em 1h)
6. Log de uso registrado
```

---

### 4. APIs NECESSÁRIAS

#### Backend FastAPI — Endpoints

| Método | Rota | Descrição | Plano |
|--------|------|-----------|-------|
| POST | `/api/auth/register` | Cadastro de usuário | FREE |
| POST | `/api/auth/login` | Login com JWT | FREE |
| POST | `/api/auth/refresh` | Refresh token | FREE |
| POST | `/api/auth/forgot-password` | Recuperação de senha | FREE |
| GET | `/api/auth/me` | Dados do usuário logado | FREE |
| POST | `/api/resumes/upload` | Upload de PDF/DOCX/TXT | FREE |
| GET | `/api/resumes/` | Lista currículos do usuário | FREE |
| GET | `/api/resumes/{id}` | Detalhe de um currículo | FREE |
| DELETE | `/api/resumes/{id}` | Remove currículo (LGPD) | FREE |
| POST | `/api/jobs/search` | Busca vagas em portais | FREE/PRO/ELITE |
| POST | `/api/jobs/manual` | Adiciona vaga manualmente | FREE |
| GET | `/api/jobs/` | Lista vagas do usuário | FREE |
| DELETE | `/api/jobs/{id}` | Remove vaga | FREE |
| POST | `/api/analysis/` | Executa análise ATS | FREE/PRO/ELITE |
| GET | `/api/analysis/` | Lista análises do usuário | FREE |
| GET | `/api/analysis/{id}` | Detalhe de uma análise | FREE |
| POST | `/api/analysis/{id}/cover-letter` | Gera carta de apresentação | ELITE |
| GET | `/api/documents/{id}/download` | Download DOCX otimizado | PRO/ELITE |
| POST | `/api/payments/checkout` | Cria sessão Stripe Checkout | FREE |
| POST | `/api/payments/webhook` | Webhook do Stripe | SYSTEM |
| POST | `/api/payments/portal` | Portal de gestão de assinatura | PRO/ELITE |
| GET | `/api/strategy/weekly` | Estratégia semanal personalizada | ELITE |
| GET | `/api/usage/` | Relatório de uso do usuário | FREE |
| DELETE | `/api/account/` | Exclusão total de dados (LGPD) | FREE |
| GET | `/api/health` | Health check | SYSTEM |

#### NVIDIA API — Contratos de Chamada

**Modelo Principal: qwen/qwen3.5-122b-a10b**

| Uso | Temperature | max_tokens | Função |
|-----|------------|------------|--------|
| Análise ATS | 0.3 | 8192 | Score + gaps + recomendações |
| Reescrita de Resumo | 0.6 | 4096 | Resumo executivo otimizado |
| Carta de Apresentação | 0.7 | 4096 | Cover letter personalizada |
| Estratégia Semanal | 0.8 | 6144 | Plano de ação semanal |
| Auto-Apply | 0.2 | 2048 | Preenchimento de campos |

---

### 5. MONETIZAÇÃO

#### Planos e Preços (BRL/mês)

| Feature | FREE | PRO (R$49) | ELITE (R$149) |
|---------|------|-----------|---------------|
| Análises ATS/dia | 3 | 15 | Ilimitado |
| Vagas buscadas/dia | 3 | 15 | Ilimitado |
| Currículo adaptado auto | ✗ | ✔ | ✔ |
| Exportação DOCX premium | ✗ | ✔ | ✔ |
| Dashboard estratégico | Básico | Completo | Completo |
| Carta de apresentação | ✗ | ✗ | ✔ |
| Estratégia semanal | ✗ | ✗ | ✔ |
| Multiportais (vagas) | 1 portal | 3 portais | Todos |
| Auto-apply assistido | ✗ | ✗ | ✔ |
| Suporte | Comunidade | Email | Prioritário |

#### Projeção de Receita (12 meses)

| Mês | Users FREE | Users PRO | Users ELITE | MRR (R$) |
|-----|-----------|----------|-------------|----------|
| M1 | 100 | 5 | 1 | 394 |
| M3 | 500 | 30 | 5 | 2.195 |
| M6 | 2.000 | 120 | 20 | 8.880 |
| M12 | 8.000 | 500 | 60 | 32.390 |

#### Conversão Esperada
- FREE → PRO: 6-8%
- PRO → ELITE: 4-5%
- Churn mensal: <5%

---

### 6. SEGURANÇA LGPD

#### Princípios Implementados

1. **Minimização de Dados**: Coletamos apenas o necessário para o serviço
2. **Consentimento**: Checkbox obrigatório no cadastro com link dos Termos
3. **Transparência**: Política de privacidade acessível em todas as páginas
4. **Portabilidade**: API `/api/account/export` exporta todos os dados do usuário
5. **Eliminação**: API `DELETE /api/account/` remove TUDO em até 72h
6. **Anonimização**: Logs de uso anonimizados após 90 dias
7. **Criptografia**: Dados em trânsito (HTTPS) e em repouso (Supabase pgcrypto)

#### Implementação Técnica
```python
# api/app/utils/lgpd.py
class LGPDCompliance:
    # Exclusão total de dados do usuário
    async def delete_user_data(user_id: UUID):
        # 1. Remove de todas as tabelas
        # 2. Remove arquivos do Storage
        # 3. Remove conta de autenticação
        # 4. Registra exclusão no audit_log
        # 5. Envia email de confirmação

    # Exportação de dados (portabilidade)
    async def export_user_data(user_id: UUID):
        # Retorna JSON com TODOS os dados do usuário
        # Inclui: perfil, currículos, vagas, análises, uso

    # Consentimento
    async def record_consent(user_id: UUID, consent_type: str):
        # Registra data, IP e versão dos termos
```

#### Dados Sensíveis
- Currículos: criptografados no Storage
- Dados bancários: nunca tocam nosso servidor (Stripe)
- IP: anonimizado após 90 dias
- Logs: retidos por 1 ano (obrigação legal), depois purgados

---

### 7. ROADMAP MVP → SCALE

#### MVP (Semanas 1-4)
- [x] Arquitetura técnica completa
- [x] Backend FastAPI com auth + análise ATS
- [x] Frontend: Landing + Login + Dashboard + Upload + Análise
- [x] NVIDIA API integração (análise ATS)
- [x] Parse de PDF/DOCX/TXT
- [x] Supabase Auth + DB migrations
- [ ] Deploy: Vercel + Railway

#### V1.0 (Semanas 5-8)
- [x] Stripe integration (assinaturas)
- [x] Geração DOCX premium
- [ ] Busca de vagas (1 portal: Indeed)
- [x] Dashboard estratégico (PRO)
- [x] Rate limiting por plano
- [ ] LGPD: exclusão + exportação

#### V1.5 (Semanas 9-12)
- [ ] Multiportais (LinkedIn + Glassdoor)
- [x] Carta de apresentação (ELITE)
- [x] Estratégia semanal (ELITE)
- [ ] Auto-apply assistido (ELITE)
- [ ] Email marketing automatizado
- [ ] Analytics dashboard para admin

#### V2.0 (Meses 4-6)
- [ ] Multi-idioma (EN + ES)
- [ ] API pública para parceiros
- [ ] Chrome Extension para auto-apply
- [ ] Mobile app (React Native)
- [ ] Multi-region deploy (US + EU)
- [ ] SOC 2 compliance

#### SCALE (Meses 7-12)
- [ ] Marketplace de templates de currículo
- [ ] Integração com ATS corporativos
- [ ] AI Career Coach (chatbot 24/7)
- [ ] Networking inteligente
- [ ] White-label para recruiters
- [ ] Series A readiness

---

### 8. CUSTOS OPERACIONAIS

#### Custos Mensais (MVP — ~500 users)

| Serviço | Custo (R$) | Detalhe |
|---------|-----------|---------|
| Supabase Free | 0 | 500MB DB, 1GB Storage, 50K auth |
| Vercel Free | 0 | 100GB bandwidth |
| Railway | 30 | 1 vCPU, 2GB RAM |
| Redis (Upstash) | 0 | Free tier 10K commands/dia |
| NVIDIA API | ~50 | ~5K chamadas/mês (free tier disponível) |
| Stripe | 0 | 4.99% por transação apenas |
| Domínio | 10 | .com.br anual |
| **Total MVP** | **~90/mês** | |

#### Custos Mensais (Scale — ~5.000 users)

| Serviço | Custo (R$) | Detalhe |
|---------|-----------|---------|
| Supabase Pro | 100 | 8GB DB, 100GB Storage |
| Vercel Pro | 75 | 1TB bandwidth |
| Railway (2x) | 120 | 4 vCPU, 8GB RAM |
| Redis (Upstash) | 50 | Pay-as-you-go |
| NVIDIA API | 500 | ~50K chamadas/mês |
| SendGrid | 60 | Email transacional |
| Monitoring | 30 | Sentry + Uptime |
| CDN/Storage | 50 | Arquivos de usuários |
| **Total Scale** | **~985/mês** | |

#### Break-even: ~15 usuários PRO + 3 ELITE = R$1.197/mês

---

### 9. COMO EVITAR OVERLOAD NO BANCO

#### Estratégias Implementadas

1. **Connection Pooling**: Supabase gerencia pool automaticamente (max 60 conexões)
2. **Read Replicas**: Queries de leitura vão para replica (Supabase automaticamente)
3. **Redis Cache**: Resultados de análise cacheados por 24h (mesmo CV + mesma vaga = cache hit)
4. **Paginação**: Todas as listas usam cursor-based pagination (limit/offset otimizado)
5. **JSONB Indexes**: GIN indexes em colunas JSONB para queries rápidas
6. **Partitioning**: `usage_logs` particionada por mês automaticamente
7. **Archival**: Análises com >90 dias movidas para tabela `optimization_results_archive`
8. **Rate Limiting**: Por plano + Redis sliding window
9. **Lazy Loading**: Frontend carrega dados sob demanda (infinite scroll)
10. **CDN para Arquivos**: Supabase Storage + CDN para DOCX/PDF

#### Queries Otimizadas
```sql
-- Índice composto para query mais comum (dashboard)
CREATE INDEX idx_optimization_user_created ON optimization_results(user_id, created_at DESC);

-- GIN index para busca em JSONB (missing_skills)
CREATE INDEX idx_optimization_skills ON optimization_results USING GIN (missing_skills);

-- Partial index para currículos ativos
CREATE INDEX idx_resumes_active ON resumes(user_id) WHERE is_active = true;
```

---

### 10. COMO DEIXAR RÁPIDO E PREMIUM

#### Performance Frontend
- **Vite + SWC**: Build em <2s, HMR instantâneo
- **Framer Motion**: Animações GPU-aceleradas (transform, opacity)
- **React.lazy + Suspense**: Code splitting por página
- **Image Optimization**: WebP com fallback, lazy loading
- **Prefetching**: Prefetch de dados do dashboard ao hover no link
- **Skeleton Loading**: Placeholders animados durante carregamento

#### Performance Backend
- **FastAPI Async**: Non-blocking I/O, ~10K requests/min por worker
- **Redis Cache**: Cache de análise ATS (TTL 24h), sessões (TTL 30min)
- **Celery Workers**: Análises em background, não bloqueiam a API
- **Streaming**: Resposta da IA via SSE (Server-Sent Events) para UX instantânea
- **GZIP**: Compressão automática de responses JSON
- **Connection Reuse**: HTTP/2 keep-alive para NVIDIA API

#### UX Premium
- **Tempo de percepção <100ms**: Skeleton + optimistic updates
- **Análise progressiva**: Score aparece primeiro, detalhes carregam depois
- **Toast notifications**: Feedback visual para toda ação
- **Keyboard shortcuts**: Ctrl+Enter para análise, Ctrl+S para download
- **Dark/Light mode**: Respeita preferência do sistema
- **Responsivo**: Mobile-first, funciona perfeitamente em qualquer tela

#### Métricas de Performance Alvo
| Métrica | Alvo | Como |
|---------|------|------|
| First Contentful Paint | <1.5s | Vite + CDN |
| Time to Interactive | <3s | Code splitting |
| API Response (cache hit) | <50ms | Redis |
| API Response (IA analysis) | <15s | Streaming SSE |
| DOCX Generation | <5s | Template pré-compilado |
| Job Search | <10s | Scraping paralelo |

---

**Status: FASE 10 implementada — Motor ATS Híbrido (local + IA), Job Search 9 portais, LinkedIn Auditor, DOCX Premium, Frontend Premium UI v3.0**
**Próximo passo: Deploy (Vercel + Railway), teste E2E real, LGPD utils, Supabase real credentials**
