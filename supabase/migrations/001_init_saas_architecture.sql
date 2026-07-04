-- ================================================================
-- JARVIS CV
-- ARQUIVO: 001_init_saas_architecture.sql
-- DESCRIÇÃO: Schema core para SaaS de Otimização de Carreira (MVP-First)
-- AUTOR: SILVANO MORAES DE SOUZA
-- VERSÃO: 1.0.0
-- ================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PERFIS DE USUÁRIO (SaaS Multi-tenancy)
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_id UUID UNIQUE NOT NULL, -- Link com Supabase Auth
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    current_role TEXT,
    linkedin_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. CURRÍCULOS VERSIONADOS (Data-First Approach)
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content JSONB NOT NULL, -- Estrutura flexível para diferentes modelos de CV
    raw_text TEXT, -- Texto extraído para processamento de IA
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_version UNIQUE (user_id, version_number)
);

-- 3. PERFIL LINKEDIN (Análise de Presença Digital)
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

-- 4. VAGAS ALVO (Job Target)
CREATE TABLE target_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    company TEXT,
    description TEXT NOT NULL,
    url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. RESULTADOS DE OTIMIZAÇÃO (Syllogistic Match)
CREATE TABLE optimization_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id),
    job_id UUID REFERENCES target_jobs(id),
    score DECIMAL(5,2),
    gap_analysis JSONB, -- O que falta no CV/LinkedIn para a vaga
    suggestions JSONB, -- Sugestões de reescrita
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXAÇÃO PARA PERFORMANCE
CREATE INDEX idx_profiles_auth ON profiles(auth_id);
CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_optimization_user ON optimization_results(user_id);
CREATE INDEX idx_job_user ON target_jobs(user_id);

-- SEGURANÇA RLS (Row Level Security)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE linkedin_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE target_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE optimization_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own profile" ON profiles FOR ALL USING (auth.uid() = auth_id);
CREATE POLICY "Users can manage own resumes" ON resumes FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = resumes.user_id));
CREATE POLICY "Users can manage own linkedin" ON linkedin_snapshots FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = linkedin_snapshots.user_id));
CREATE POLICY "Users can manage own jobs" ON target_jobs FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = target_jobs.user_id));
CREATE POLICY "Users can manage own results" ON optimization_results FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = optimization_results.user_id));
