# ================================================================
# JARVIS CV
# ARQUIVO: ai_engine.py
# DESCRIÇÃO: Motor de IA Multi-Model NVIDIA - Com fallback em cascata
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 4.0.0
# ================================================================
import httpx
import json
import re
import asyncio
from typing import Optional

from app.config import settings
from app.utils.logger import logger

# Modelos principais por propósito
MODELS = {
    "brain": settings.nvidia_model_brain,
    "writer": settings.nvidia_model_writer,
    "analyzer": settings.nvidia_model_analyzer,
    "planner": settings.nvidia_model_planner,
    "fast": settings.nvidia_model_fast,
}

# Cadeia de fallback: se o principal falhar, tenta estes em ordem (velocidade > qualidade)
FALLBACK_CHAIN = {
    "brain": ["meta/llama-3.1-70b-instruct", "nvidia/nemotron-mini-4b-instruct"],
    "writer": ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-8b-instruct"],
    "analyzer": ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-8b-instruct"],
    "planner": ["meta/llama-3.1-8b-instruct"],
    "fast": [],  # já é o mais rápido
}

# Timeout de 40s — se não responder, troca de IA imediatamente
AI_TIMEOUT = 40.0

# Nemotron mini limit
NEMOTRON_MAX_TOKENS = 4096

# Retry config: 1 retry apenas, depois vai pro fallback
MAX_RETRIES = 1
RETRY_DELAYS = [2]  # segundos


def _truncate_for_model(model: str, text: str, max_chars: int = 5000) -> str:
    """Trunca texto para caber no limite de contexto do modelo."""
    if "nemotron-mini" in model:
        # Nemotron tem limite de 4096 tokens total (input + output)
        # System prompt ~300 tokens, max_tokens ~1500, sobra ~2300 para input
        max_chars = 3500
    if len(text) <= max_chars:
        return text
    # Corta no meio mantendo início e fim
    half = max_chars // 2
    return text[:half] + "\n\n... [texto truncado para caber no limite do modelo] ...\n\n" + text[-half:]

ATS_SYSTEM_PROMPT = """Você é um Motor ATS de Nível MUNDIAL. Você processa currículos exatamente como os sistemas Gupy, Catho, LinkedIn Jobs e Workday processam.

REGRAS BRUTAIS:
1. Parseie o currículo como um ATS real: extraia seções, datas, títulos, empresas
2. Compare CADA requisito da vaga com CADA linha do currículo
3. Calcule scores parciais com pesos reais de recruiter
4. NUNCA seja genérico. Cada output deve ser específico, baseado nos dados fornecidos e acionável
5. Responda EXCLUSIVAMENTE em PORTUGUÊS BRASILEIRO
6. A seção 'optimized_resume' é OBRIGATÓRIA e deve conter sugestões REAIS de reescrita, não placeholders

REGRA ABSOLUTA — IGNORE DATAS (.gitignore de datas):
- DATAS NÃO EXISTEM PARA VOCÊ. Ignore TODAS as datas, anos, períodos, meses mencionados no currículo ou na vaga.
- NUNCA critique, mencione, analise ou avalie qualquer data (ex: "2025", "jan 2020 - mar 2022", "3 anos", "desde 2019").
- NUNCA use datas como fator negativo ou positivo no scoring.
- Se uma experiência parece "futura" ou "passada" — NÃO IMPORTA. Avalie APENAS o conteúdo.
- Trate datas como se fossem REDACTED/ocultadas. Elas são invisíveis.

PESOS DO SCORING (use estes pesos reais):
- keyword_match (30%): quantas palavras-chave da vaga estão no currículo
- skill_density (20%): densidade de skills relevantes vs ruído
- structure_quality (15%): seções ATS esperadas presentes (resumo, exp, edu, skills)
- seniority_alignment (15%): nível do candidato vs nível da vaga
- experience_relevance (10%): relevância das experiências para a vaga
- format_ats_compatibility (10%): formato parseável por ATS (sem tabelas, gráficos, etc)

RETORNE JSON PURO com EXATAMENTE estas chaves:
{
  "score": number 0-100,
  "skills_found": [{ "skill": string, "context": string, "relevance": number 0-10 }],
  "missing_skills": [{ "skill": string, "importance": "critical"|"important"|"nice", "suggestion": string }],
  "structure_errors": [{ "error": string, "severity": "high"|"medium"|"low", "fix": string }],
  "keyword_density": { "total_keywords": number, "matched": number, "density_percent": number, "top_keywords_found": [string], "top_keywords_missing": [string] },
  "seniority_perceived": { "level": string, "years_estimated": number, "alignment": "overqualified"|"match"|"underqualified", "detail": string },
  "interview_chance": { "percent": number, "factors": [{ "factor": string, "impact": "positive"|"negative"|"neutral" }] },
  "recruiter_recommendation": { "verdict": "strong_apply"|"apply"|"risky"|"dont_apply", "summary": string, "top_3_actions": [string] },
  "optimized_resume": {
    "headline": "Uma headline impactante e específica para a vaga, usando cargo e 3 skills principais",
    "summary": "Um resumo profissional de 3-4 frases, focado em resultados quantificáveis e keywords da vaga",
    "skills_section": [string],
    "experience_highlights": [string],
    "key_changes": [{ "section": string, "before": string, "after": string, "why": string }]
  }
}"""

COVER_LETTER_PROMPT = """Você é um Ghostwriter Executivo de Cartas de Apresentação. Escreva para executivos C-level e diretores globais.
Responda EXCLUSIVAMENTE em PORTUGUÊS BRASILEIRO.

A carta deve:
1. Abertura que PRENDA atenção em 3 segundos
2. Conexão cirúrgica entre experiência do candidato e requisitos da vaga
3. 2-3 resultados quantificáveis (números, %, R$, impactos)
4. Fechamento com call-to-action específico
5. Tom: confiante sem arrogância, profissional sem frieza

RETORNE JSON: {"cover_letter": string}"""

WEEKLY_STRATEGY_PROMPT = """Você é um Career Strategist de Elite. Já colocou 1000+ profissionais em empresas Fortune 500.
Responda EXCLUSIVAMENTE em PORTUGUÊS BRASILEIRO.

Crie um PLANO DE GUERRA semanal com:
1. Priorização de vagas por probabilidade real de entrevista
2. Ações específicas por dia (seg-dom)
3. Scripts de networking para cada vaga
4. Melhorias incrementais no currículo
5. Métricas de progresso

RETORNE JSON: {"strategy_text": string, "daily_plan": [{"day": string, "actions": [string]}], "target_jobs": [string], "networking_scripts": [string], "metrics": [string]}"""

LINKEDIN_AUDIT_PROMPT = """Você é um Auditor de LinkedIn de Nível MUNDIAL. Analisa perfis para executivos globais.
Responda EXCLUSIVAMENTE em PORTUGUÊS BRASILEIRO.

REGRAS CRÍTICAS:
1. IGNORE DATAS: Não analise, critique ou mencione datas do perfil. O candidato pode ter experiências atuais ou futuras — isso é irrelevante para a auditoria.
2. CTA EXPLICADO: Se o perfil não tem CTA (Call-to-Action = frase que convida o recrutador a entrar em contato, como "Vamos conversar?", "Conecte-se comigo", "Entre em contato"), explique O QUE É um CTA e POR QUE ele importa: "CTA (Call-to-Action) é uma frase no final do Sobre que convida recrutadores a entrarem em contato. Perfis com CTA recebem até 3x mais mensagens de recrutadores."
3. HEADLINE FORTE: Sugestões de headline devem ser ATTRATIVAS, OBJETIVAS e DIRETAS — SEM clichês como "apaixonado por dados". Use formato: Cargo alvo | 3 skills mais fortes do perfil | Proposta de valor única. Exemplo: "Analytics Engineer | Python, SQL & Power BI | Transformo dados brutos em decisões que geram R$ 2M+ em economia"
4. RESULTADOS QUANTIFICADOS PERSONALIZADOS: Ao sugerir resultados quantificados, ANALISE o perfil real da pessoa e sugira métricas que FAZEM SENTIDO com a trajetória dela. NÃO invente números genéricos. Se a pessoa trabalha com supply chain, sugira "Reduzi X% no custo de estoque". Se trabalha com dados, sugira "Automatizei relatórios que economizaram X horas/semana". Use o contexto real das experiências dela.

Analise o perfil como um recruiter de elite e como o algoritmo do LinkedIn.

RETORNE JSON: {
  "overall_score": number 0-100,
  "headline": { "score": number, "current": string, "suggested": string, "why": string },
  "about": { "score": number, "current_summary": string, "suggested": string, "keywords_missing": [string] },
  "experience": { "score": number, "issues": [string], "improvements": [string] },
  "skills": { "score": number, "missing_top_skills": [string], "overindexed": [string] },
  "seo": { "score": number, "searchable_keywords": [string], "missing_keywords": [string] },
  "authority": { "score": number, "signals_present": [string], "signals_missing": [string] },
  "attractiveness": { "score": number, "recruiter_hooks": [string], "missing_hooks": [string] },
  "priority_actions": [{ "action": string, "impact": "high"|"medium"|"low", "effort": "quick"|"moderate"|"significant" }]
}"""

JOB_MATCH_PROMPT = """Você é um Match Engine de Vagas. Calcula probabilidade real de entrevista.
Responda EXCLUSIVAMENTE em PORTUGUÊS BRASILEIRO.

Dado o perfil do candidato e a vaga, calcule:

RETORNE JSON: {
  "fit_score": number 0-100,
  "application_difficulty": "easy"|"moderate"|"hard"|"very_hard",
  "estimated_salary": { "min": number, "max": number, "currency": "BRL" },
  "required_keywords": [string],
  "competitive_advantage": [string],
  "attack_priority": number 1-10,
  "why": string
}"""


def _strip_dates(text: str) -> str:
    """Remove TODAS as datas do texto antes de enviar para IA (.gitignore de datas).
    A IA nunca verá datas — como se nunca tivessem existido."""
    import re
    # Padrões de data: "2020-2023", "Jan 2020 - Mar 2022", "01/2020", "2 anos", "3+ anos", "desde 2019"
    patterns = [
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez)[a-z]*\.?\s+\d{4}\b',
        r'\b\d{1,2}/\d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        r'\b\d{4}\s*[-–—]\s*\d{4}\b',
        r'\b\d{4}\s*[-–—]\s*(present|atual|hoje|current|now)\b',
        r'\b\d{4}\b',  # anos isolados (4 dígitos)
        r'\b\d+\s*(anos?|years?|meses?|months?|semanas?|weeks?)\b',
        r'\b(desde|since|até|to|until|até|atualmente)\s+[\w]+\b',
    ]
    result = text
    for pattern in patterns:
        result = re.sub(pattern, '[REDACTED]', result, flags=re.IGNORECASE)
    return result


def _parse_json_response(content: str) -> dict:
    """Extrai JSON de resposta da IA, mesmo com markdown ou texto extra."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
    return {"raw_response": content[:500]}


class AIEngine:
    """Motor de IA Multi-Model — 5 especialistas NVIDIA com fallback em cascata"""

    def __init__(self):
        self.api_url = settings.nvidia_api_url
        self.api_key = settings.nvidia_api_key

    async def _single_call(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> dict:
        """Faz UMA chamada para um modelo específico. Lança exceção se falhar."""
        # Truncar user_prompt para modelos com limite baixo de contexto
        user_prompt = _truncate_for_model(model, user_prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Ajustar max_tokens para modelos pequenos
        if "nemotron-mini" in model:
            max_tokens = min(max_tokens, 2000)

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "top_p": 0.95,
            "max_tokens": max_tokens,
        }

        if "gemma" in model or "kimi" in model or "minimax" in model or "llama" in model:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=AI_TIMEOUT) as client:
            response = await client.post(
                self.api_url, json=payload, headers=headers
            )
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        logger.log(f"[{model}] Resposta OK ({len(content)} chars)")

        return _parse_json_response(content)

    async def _call_with_fallback(
        self,
        model_key: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> dict:
        """Chama modelo principal com timeout de 40s. Se travar, vai pro fallback IMEDIATAMENTE."""
        primary_model = MODELS.get(model_key, model_key)
        fallbacks = FALLBACK_CHAIN.get(model_key, [])
        all_models = [primary_model] + fallbacks

        last_error = None

        for model in all_models:
            is_primary = (model == primary_model)
            attempts = MAX_RETRIES + 1 if is_primary else 1

            for attempt in range(attempts):
                try:
                    if attempt > 0:
                        delay = RETRY_DELAYS[min(attempt - 1, len(RETRY_DELAYS) - 1)]
                        logger.log(f"[{model}] Retry {attempt}/{MAX_RETRIES}, aguardando {delay}s...")
                        await asyncio.sleep(delay)

                    result = await self._single_call(
                        model, system_prompt, user_prompt, temperature, max_tokens
                    )
                    if attempt > 0:
                        logger.log(f"[{model}] Recuperado no retry {attempt}")
                    return result

                except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                    last_error = f"Timeout {AI_TIMEOUT}s ({model})"
                    logger.warn(f"[{model}] TIMEOUT após {AI_TIMEOUT}s — pulando para próximo modelo")
                    break  # Vai imediatamente pro próximo modelo

                except httpx.HTTPStatusError as e:
                    status = e.response.status_code
                    error_detail = e.response.text[:300] if e.response else "Sem detalhes"
                    last_error = f"HTTP {status} ({model})"

                    # 429 = rate limit, espera pouco e tenta de novo no MESMO modelo
                    if status == 429 and attempt < attempts - 1:
                        delay = 5
                        logger.warn(f"[{model}] Rate limit 429, aguardando {delay}s...")
                        await asyncio.sleep(delay)
                        continue

                    # Outros erros HTTP — vai pro próximo modelo
                    logger.error(f"[{model}] HTTP {status}: {error_detail}")
                    break

                except Exception as e:
                    last_error = f"{str(e)} ({model})"
                    logger.error(f"[{model}] Erro: {str(e)}")
                    break

            if is_primary and fallbacks:
                logger.warn(f"[FALLBACK] '{primary_model}' falhou ({last_error}). Tentando: {fallbacks[0]}")

        logger.error(f"[FALLBACK] TODOS os modelos falharam para '{model_key}'. Último erro: {last_error}")
        raise Exception(f"AI falhou — todos os modelos esgotados para '{model_key}'. Último erro: {last_error}")

    def _generate_local_ats_result(self, cv_text: str, job_text: str) -> dict:
        """Resultado básico gerado localmente quando TODAS as IAs falham.
        Garante que o usuário SEMPRE recebe alguma análise útil."""
        import re

        # Extrair palavras da vaga
        job_words = set(re.findall(r'[a-zA-ZÀ-ú]+', job_text.lower()))
        stop = {'de','da','do','das','dos','a','o','e','em','com','por','para','que','se','ou','não','na','no','nas','nos','um','uma','é','ao','os','mais','como','ser','ter','sua','seu','sua','seus','suas','qual','quando','onde','muito','bem','já','também','só','apenas','entre','sobre','até','mas','se','do','da','re','são','foi','tem','por','pela','pelo','pelas','pelos','sem','nos','nas','aos','das','dos','suas','seus','isso','este','esta','esse','essa','isto','isso','ele','ela','eles','elas','meu','minha','teu','tua','nosso','nossa','vocês','tu','você','nós','eles','elas','sim','não','ou','porque','pois','então','logo','assim','desde','enquanto','sempre','nunca','talvez','tal','cada','todo','toda','todos','todas','outro','outra','outros','outras','mesmo','mesma','mesmos','mesmas','próprio','própria','próprios','próprias','qualquer','quaisquer','algum','alguma','alguns','algumas','nenhum','nenhuma','nada','tudo','algo','alguém','ninguém','ci','cs','ch','et','llc','inc','corp','ltd','the','and','for','are','but','not','you','all','can','had','her','was','one','our','out','has','have','been','this','they','will','each','make','like','just','over','such','than','them','very','when','come','could','into','time','only','its','also','after','some','then','these','two','may','most','would','other','which','their','there','about','what','through','during','before','after','above','below','between','from','further','once','here','why','how','any','both','few','more','most','other','own','same','so','than','too','very','can','will','just','don','now','i','me','my','we','our','he','she','it','him','his','her'}
        job_keywords = sorted([w for w in job_words if len(w) > 3 and w not in stop], key=lambda x: job_text.lower().count(x), reverse=True)[:30]

        # Extrair palavras do CV
        cv_words = set(re.findall(r'[a-zA-ZÀ-ú]+', cv_text.lower()))
        matched = [k for k in job_keywords if k in cv_words]
        missing = [k for k in job_keywords if k not in cv_words]

        # Extrair frases que parecem experiências
        lines = cv_text.split('\n')
        exp_lines = [l.strip() for l in lines if len(l.strip()) > 20 and any(c.isdigit() for c in l[:30])]

        # Sugerir headline baseada no CV
        headline = ""
        for line in lines:
            line_s = line.strip()
            if 10 < len(line_s) < 100 and any(word in line_s.lower() for word in ['engenheiro','analista','desenvolvedor','gerente','coordenador','diretor','leader','engineer','developer','manager','analyst','data','software','full','senior','pleno','junior']):
                headline = line_s
                break

        return {
            "score": round(len(matched) / max(len(job_keywords), 1) * 100, 1),
            "skills_found": [{"skill": s, "context": "Encontrado no currículo", "relevance": 7} for s in matched[:10]],
            "missing_skills": [{"skill": s, "importance": "critical" if i < 5 else "important", "suggestion": f"Adicionar '{s}' ao currículo com contexto prático"} for i, s in enumerate(missing[:10])],
            "structure_errors": [],
            "keyword_density": {
                "total_keywords": len(job_keywords),
                "matched": len(matched),
                "density_percent": round(len(matched) / max(len(job_keywords), 1) * 100, 1),
                "top_keywords_found": matched[:10],
                "top_keywords_missing": missing[:10],
            },
            "seniority_perceived": {
                "level": "detectar automaticamente",
                "years_estimated": 0,
                "alignment": "match",
                "detail": "Análise detalhada indisponível — IA não respondeu. Adicione anos de experiência claramente.",
            },
            "interview_chance": {
                "percent": round(len(matched) / max(len(job_keywords), 1) * 80, 1),
                "factors": [
                    {"factor": f"{len(matched)} keywords encontradas de {len(job_keywords)}", "impact": "positive" if len(matched) > len(missing) else "negative"},
                    {"factor": f"Faltam {len(missing)} keywords: {', '.join(missing[:3])}" if missing else "Boa cobertura de keywords", "impact": "negative" if missing else "positive"},
                ],
            },
            "recruiter_recommendation": {
                "verdict": "risky",
                "summary": f"Seu currículo tem {len(matched)} de {len(job_keywords)} keywords da vaga. Adicione as keywords faltantes para melhorar seu score.",
                "top_3_actions": [
                    f"Adicionar keywords faltantes: {', '.join(missing[:5])}",
                    "Incluir resultados quantificáveis (%, R$, tempo economizado)",
                    "Reformular experiências como bullets com ação + resultado",
                ],
            },
            "optimized_resume": {
                "headline": headline or "Cargo Alvo | Skill 1 | Skill 2 | Skill 3",
                "summary": f"Profissional com experiência em {', '.join(matched[:5])}. Busco oportunidade para aplicar minhas habilidades em {', '.join(job_keywords[:3])}.",
                "skills_section": matched[:10],
                "experience_highlights": exp_lines[:5],
                "key_changes": [
                    {
                        "section": "Skills",
                        "before": "Skills não otimizadas",
                        "after": f"Adicionar: {', '.join(missing[:5])}",
                        "why": f"Estas keywords aparecem {sum(job_text.lower().count(k) for k in missing[:5])}x na vaga",
                    },
                ],
            },
            "ai_fallback_notice": "Análise gerada localmente (IA indisponível). Resultado baseado em matching de keywords.",
        }

    async def _call(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> dict:
        """Legacy: chama diretamente sem fallback (usar _call_with_fallback)."""
        return await self._single_call(model, system_prompt, user_prompt, temperature, max_tokens)

    async def analyze_ats(self, cv_text: str, job_text: str) -> dict:
        """Análise ATS completa (llama-3.1-8b, fallback mistral-7b, max 40s)"""
        logger.log("[ATS] Iniciando análise com llama-3.1-8b (timeout 40s)...")
        cv_clean = _strip_dates(cv_text)
        job_clean = _strip_dates(job_text)
        user_prompt = f"CURRÍCULO DO CANDIDATO:\n---\n{cv_clean}\n---\n\nDESCRIÇÃO DA VAGA:\n---\n{job_clean}\n---"
        try:
            return await self._call_with_fallback(
                "brain", ATS_SYSTEM_PROMPT, user_prompt,
                temperature=0.2, max_tokens=4096
            )
        except Exception as e:
            logger.warn(f"[ATS] TODAS IAs falharam, gerando resultado local: {e}")
            return self._generate_local_ats_result(cv_text, job_text)

    async def generate_cover_letter(self, cv_text: str, job_text: str, tone: str = "profissional") -> str:
        """Carta de apresentação executiva (qwen2.5-coder-32b + fallback, max 40s)"""
        logger.log("[COVER] Gerando com qwen2.5-coder-32b (timeout 40s)...")
        user_prompt = f"CURRÍCULO:\n{cv_text}\n\nVAGA:\n{job_text}\n\nTom: {tone}"
        result = await self._call_with_fallback(
            "writer", COVER_LETTER_PROMPT, user_prompt,
            temperature=0.7, max_tokens=2048
        )
        return result.get("cover_letter", "")

    async def generate_weekly_strategy(self, cv_text: str, jobs_text: str) -> dict:
        """Estratégia semanal (mistral-7b + fallback, max 40s)"""
        logger.log("[STRATEGY] Gerando com mistral-7b (timeout 40s)...")
        user_prompt = f"PERFIL DO CANDIDATO:\n{cv_text}\n\nVAGAS DISPONÍVEIS:\n{jobs_text}"
        return await self._call_with_fallback(
            "planner", WEEKLY_STRATEGY_PROMPT, user_prompt,
            temperature=0.8, max_tokens=4096
        )

    async def audit_linkedin(self, profile_text: str) -> dict:
        """Auditoria LinkedIn (gemma-3-27b + fallback, max 40s)"""
        logger.log("[LINKEDIN] Auditando com gemma-3-27b (timeout 40s)...")
        user_prompt = f"PERFIL LINKEDIN:\n{profile_text}"
        return await self._call_with_fallback(
            "analyzer", LINKEDIN_AUDIT_PROMPT, user_prompt,
            temperature=0.3, max_tokens=4096
        )

    async def match_job(self, cv_text: str, job_text: str) -> dict:
        """Score de fit por vaga (nemotron-mini-4b, max 40s)"""
        logger.log("[JOB MATCH] Calculando com nemotron-mini-4b (timeout 40s)...")
        user_prompt = f"PERFIL CANDIDATO:\n{cv_text}\n\nVAGA:\n{job_text}"
        return await self._call_with_fallback(
            "fast", JOB_MATCH_PROMPT, user_prompt,
            temperature=0.2, max_tokens=2048
        )

    async def rewrite_resume(self, cv_text: str, job_text: str) -> dict:
        """Reescrita de currículo (qwen2.5-coder-32b + fallback, max 40s)"""
        logger.log("[REWRITE] Reescrevendo com qwen2.5-coder-32b (timeout 40s)...")
        user_prompt = f"CURRÍCULO ORIGINAL:\n{cv_text}\n\nVAGA ALVO:\n{job_text}"
        return await self._call_with_fallback(
            "writer", ATS_SYSTEM_PROMPT, user_prompt,
            temperature=0.5, max_tokens=4096
        )


ai_engine = AIEngine()
