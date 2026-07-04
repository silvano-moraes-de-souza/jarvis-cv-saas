-- ================================================================
-- JARVIS CV
-- ARQUIVO: 002_saas_plans_subscriptions.sql
-- DESCRIÇÃO: Schema SaaS completo - Planos, assinaturas, logs, estratégias, RLS
-- AUTOR: SILVANO MORAES DE SOUZA
-- VERSÃO: 2.0.0
-- ================================================================

-- 1. TABELA DE PLANOS (Catálogo de planos disponíveis)
CREATE TABLE IF NOT EXISTS plans (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price_monthly DECIMAL(10,2) NOT NULL DEFAULT 0,
    daily_analyses_limit INTEGER NOT NULL DEFAULT 3,
    daily_jobs_limit INTEGER NOT NULL DEFAULT 3,
    features JSONB NOT NULL DEFAULT '[]',
    stripe_price_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO plans (id, name, price_monthly, daily_analyses_limit, daily_jobs_limit, features) VALUES
    ('free', 'Gratuito', 0.00, 3, 3,
     '["Análise ATS básica", "3 análises/dia", "3 vagas/dia", "Upload de currículo"]'),
    ('pro', 'Profissional', 49.00, 15, 15,
     '["Tudo do Gratuito", "15 análises/dia", "15 vagas/dia", "Download DOCX otimizado", "Reescrita de currículo", "Suporte prioritário"]'),
    ('elite', 'Elite', 149.00, 999, 999,
     '["Tudo do Profissional", "Análises ilimitadas", "Vagas ilimitadas", "Carta de apresentação IA", "Estratégia semanal personalizada", "Auto-apply (em breve)", "Suporte VIP"]')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    price_monthly = EXCLUDED.price_monthly,
    daily_analyses_limit = EXCLUDED.daily_analyses_limit,
    daily_jobs_limit = EXCLUDED.daily_jobs_limit,
    features = EXCLUDED.features;

-- 2. ASSINATURAS (Gestão de plano ativo do usuário)
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    plan TEXT NOT NULL DEFAULT 'free' REFERENCES plans(id),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'past_due', 'trialing')),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_subscription UNIQUE (user_id)
);

-- 3. LOGS DE USO (Rate limiting e analytics)
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    feature TEXT NOT NULL CHECK (feature IN ('analysis', 'job', 'cover_letter', 'weekly_strategy', 'resume_rewrite', 'docx_download')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. ESTRATÉGIAS SEMANAIS (Plano ELITE)
CREATE TABLE IF NOT EXISTS weekly_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    strategy_text TEXT NOT NULL,
    target_jobs JSONB DEFAULT '[]',
    action_items JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_week UNIQUE (user_id, week_start)
);

-- 5. Adicionar colunas faltantes em target_jobs
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'target_jobs' AND column_name = 'company') THEN
        ALTER TABLE target_jobs ADD COLUMN company TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'target_jobs' AND column_name = 'source') THEN
        ALTER TABLE target_jobs ADD COLUMN source TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'target_jobs' AND column_name = 'location') THEN
        ALTER TABLE target_jobs ADD COLUMN location TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'target_jobs' AND column_name = 'salary_range') THEN
        ALTER TABLE target_jobs ADD COLUMN salary_range TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'target_jobs' AND column_name = 'is_remote') THEN
        ALTER TABLE target_jobs ADD COLUMN is_remote BOOLEAN DEFAULT false;
    END IF;
END $$;

-- 6. Adicionar colunas faltantes em resumes
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'resumes' AND column_name = 'file_url') THEN
        ALTER TABLE resumes ADD COLUMN file_url TEXT;
    END IF;
END $$;

-- 7. Atualizar optimization_results para nova estrutura
-- (gap_analysis e suggestions já são JSONB, mas garantimos compatibilidade)

-- 8. INDEXAÇÃO PARA PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe ON subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_user ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_feature ON usage_logs(user_id, feature);
CREATE INDEX IF NOT EXISTS idx_usage_logs_date ON usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_weekly_strategies_user ON weekly_strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_target_jobs_user ON target_jobs(user_id);

-- 9. RLS (Row Level Security) - LGPD Compliance
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE plans ENABLE ROW LEVEL SECURITY;

-- Políticas RLS
CREATE POLICY "Users can read own subscription" ON subscriptions FOR SELECT USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = subscriptions.user_id));
CREATE POLICY "Users can read own usage" ON usage_logs FOR SELECT USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = usage_logs.user_id));
CREATE POLICY "Users can manage own strategies" ON weekly_strategies FOR ALL USING (auth.uid() = (SELECT auth_id FROM profiles WHERE id = weekly_strategies.user_id));
CREATE POLICY "Plans are publicly readable" ON plans FOR SELECT USING (true);

-- Service role pode gerenciar subscriptions e usage_logs (para API backend)
CREATE POLICY "Service role manages subscriptions" ON subscriptions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role manages usage" ON usage_logs FOR ALL USING (true) WITH CHECK (true);

-- 10. FUNÇÃO: Verificar limite diário de uso
CREATE OR REPLACE FUNCTION check_daily_limit(p_user_id UUID, p_feature TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    v_plan TEXT;
    v_limit INTEGER;
    v_count INTEGER;
BEGIN
    SELECT plan INTO v_plan FROM subscriptions WHERE user_id = p_user_id AND status = 'active' LIMIT 1;
    IF NOT FOUND THEN v_plan := 'free'; END IF;

    CASE p_feature
        WHEN 'analysis' THEN SELECT daily_analyses_limit INTO v_limit FROM plans WHERE id = v_plan;
        WHEN 'job' THEN SELECT daily_jobs_limit INTO v_limit FROM plans WHERE id = v_plan;
        ELSE v_limit := 999;
    END CASE;

    SELECT COUNT(*) INTO v_count FROM usage_logs
    WHERE user_id = p_user_id AND feature = p_feature AND created_at >= CURRENT_DATE;

    RETURN v_count < v_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 11. TRIGGER: Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_subscriptions_updated ON subscriptions;
CREATE TRIGGER tr_subscriptions_updated
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS tr_profiles_updated ON profiles;
CREATE TRIGGER tr_profiles_updated
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
