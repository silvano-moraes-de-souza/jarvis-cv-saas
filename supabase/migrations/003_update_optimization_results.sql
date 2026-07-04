-- ================================================================
-- JARVIS CV
-- ARQUIVO: 003_update_optimization_results.sql
-- DESCRIÇÃO: Atualização do schema para suportar métricas de ATS e resumos
-- AUTOR: SILVANO MORAES DE SOUZA
-- VERSÃO: 1.0.0
-- ================================================================

-- Adicionando colunas específicas para maior performance de query e tipagem
ALTER TABLE optimization_results 
ADD COLUMN ats_score DECIMAL(5,2),
ADD COLUMN missing_skills JSONB DEFAULT '[]',
ADD COLUMN rewritten_summary TEXT,
ADD COLUMN improvements JSONB DEFAULT '[]';

-- Comentários para documentação do banco
COMMENT ON COLUMN optimization_results.ats_score IS 'Score de compatibilidade baseado em algoritmos de ATS';
COMMENT ON COLUMN optimization_results.missing_skills IS 'Lista de competências técnicas não encontradas no CV';
COMMENT ON COLUMN optimization_results.rewritten_summary IS 'Versão do resumo profissional otimizada para a vaga alvo';
COMMENT ON COLUMN optimization_results.improvements IS 'Sugestões acionáveis de melhoria para o currículo';
