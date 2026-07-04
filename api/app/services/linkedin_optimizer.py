# ================================================================
# JARVIS CV
# ARQUIVO: linkedin_optimizer.py
# DESCRIÇÃO: Auditor LinkedIn - Scoring determinístico 100% Python + IA apenas para sugestões
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 4.0.0
# ================================================================
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from app.config import settings
from app.utils.logger import logger
from app.utils.text_utils import normalize_text


@dataclass
class LinkedInAudit:
    overall_score: float = 0.0
    headline_score: float = 0.0
    about_score: float = 0.0
    experience_score: float = 0.0
    skills_score: float = 0.0
    seo_score: float = 0.0
    authority_score: float = 0.0
    issues: List[dict] = field(default_factory=list)
    quick_wins: List[dict] = field(default_factory=list)
    suggested_headline: str = ""
    suggested_about_opening: str = ""


class LinkedInOptimizer:
    """Auditor LinkedIn - Scoring determinístico por Python"""

    TECH_KEYWORDS = {
        "data": ["python", "sql", "power bi", "bi", "etl", "data warehouse", "data lake",
                  "pandas", "spark", "airflow", "dbt", "tableau", "looker", "analytics",
                  "machine learning", "ml", "estatística", "bigquery", "redshift", "snowflake",
                  "databricks", "dax", "power query", "data modeling", "data visualization",
                  "data pipeline", "data governance", "data cleaning", "business intelligence",
                  "kpi", "dashboard", "analytics engineering"],
        "eng": ["react", "node", "typescript", "javascript", "java", "go", "rust",
                 "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "git",
                 "api", "rest", "graphql", "microservices", "terraform", "n8n", "supabase",
                 "postgresql", "mysql", "html", "css", "tailwind", "vba", "excel"],
        "soft": ["liderança", "gestão", "comunicação", "scrum", "agile", "kanban",
                  "jira", "roadmap", "okr", "stakeholder", "backlog", "sprint",
                  "lean", "melhoria contínua", "resolução de problemas", "proatividade"],
        "business": ["supply chain", "logística", "compras", "financeiro", "custos",
                      "planejamento estratégico", "governança", "storytelling", "business analytics",
                      "análise financeira", "operações", "gestão de fornecedores", "kpi reporting"],
    }

    ACTION_VERBS = [
        "liderei", "desenvolvi", "implementei", "reduzi", "aumentei", "criei", "otimizei",
        "gerenciei", "estruturei", "transformei", "conduzi", "planejei", "executei",
        "automatizei", "migrei", "desenvolvo", "crio", "implemento", "coordeno",
        "desenvolveu", "implementou", "criou", "reduziu", "aumentou", "otimizou",
        "gerenciou", "estruturou", "transformou", "conduziu", "automatizou",
    ]

    HOOK_WORDS = [
        "apaixonado", "especialista", "com mais de", "transformo", "ajudo", "construo",
        "transformar", "especializado", "focado em", "dedicado a", "expert",
        "sólida experiência", "ampla experiência", "expertise",
    ]

    VALUE_PROPOSITION_WORDS = [
        "resultado", "impacto", "crescimento", "eficiência", "performance",
        "redução de custos", "aumento de", "melhoria", "otimização",
        "inteligência acionável", "tomada de decisão", "valor", "soluções",
    ]

    CTA_WORDS = [
        "vamos conversar", "entre em contato", "me encontre", "conecte-se",
        "fico à disposição", "open to", "disponível para", "sinta-se à vontade",
    ]

    def _score_headline(self, headline: str) -> dict:
        """Scoring determinístico de headline (max 15 pontos)"""
        score = 0
        issues = []
        norm = normalize_text(headline)

        if len(headline) > 0 and len(headline) <= 120:
            score += 3
        elif len(headline) > 120:
            issues.append({"error": "Headline maior que 120 caracteres será truncada pelo LinkedIn", "fix": "Reduza para no máximo 120 caracteres"})

        pipe_parts = [p.strip() for p in headline.split("|") if p.strip()]
        if len(pipe_parts) >= 3:
            score += 4
        elif len(pipe_parts) >= 2:
            score += 2
        else:
            issues.append({"error": "Headline sem separadores | — use formato: Cargo | Especialidade | Valor", "fix": "Separe com | para melhor leitura e SEO"})

        # Buscar keywords técnicas no headline
        all_keywords = []
        for terms in self.TECH_KEYWORDS.values():
            all_keywords.extend(terms)
        keyword_matches = [kw for kw in all_keywords if kw in norm]
        kw_score = min(len(keyword_matches) * 2, 8)
        score += kw_score

        # Penalizar "jr/junior" na headline (reduz senioridade percebida)
        if " jr" in norm or "junior" in norm or "jr." in norm:
            issues.append({"error": "'Jr/Júnior' na headline reduz sua senioridade percebida", "fix": "Remova 'Jr' e use 'Analytics Engineer' ou 'Data Analyst' para parecer mais sênior"})
            score = max(score - 2, 0)

        if not keyword_matches:
            issues.append({"error": "Nenhuma keyword técnica encontrada na headline", "fix": "Adicione 2-3 skills principais como SQL, Python ou Power BI"})

        return {"score": min(score, 15), "issues": issues, "keyword_matches": keyword_matches}

    def _score_about(self, about: str) -> dict:
        """Scoring determinístico da seção Sobre (max 20 pontos)"""
        score = 0
        issues = []
        norm = normalize_text(about)

        if len(about) < 50:
            issues.append({"error": "Seção Sobre vazia ou muito curta", "fix": "Escreva pelo menos 3 parágrafos com hook, experiência e CTA"})
            return {"score": 0, "issues": issues}

        if 200 <= len(about) <= 2600:
            score += 4
        elif len(about) < 200:
            issues.append({"error": "Seção Sobre curta demais (< 200 chars)", "fix": "Expanda com mais detalhes sobre sua experiência"})
        elif len(about) > 2600:
            issues.append({"error": "Seção Sobre muito longa (> 2600 chars)", "fix": "Reduza para 3-5 parágrafos concisos"})

        hook_words_found = [w for w in self.HOOK_WORDS if w in norm]
        if hook_words_found:
            score += 4
        else:
            issues.append({"error": "Sem hook na abertura do Sobre", "fix": "Comece com uma frase de impacto: 'Transformo dados em decisões estratégicas'"})

        all_keywords = [kw for terms in self.TECH_KEYWORDS.values() for kw in terms]
        keyword_matches = [kw for kw in all_keywords if kw in norm]
        kw_score = min(len(keyword_matches) * 0.8, 5)
        score += kw_score

        achievement_patterns = [r'\d+%', r'r\$\s*\d+', r'\d+\+?\s*(anos|projetos|equipes|clientes|pessoas)', r'\d+\+?\s*(mil|milhões)']
        has_achievements = any(re.search(p, about.lower()) for p in achievement_patterns)
        if has_achievements:
            score += 4
        else:
            issues.append({"error": "Sem resultados quantificáveis no Sobre", "fix": "Adicione números: %, R$, volume de dados, nº de projetos"})

        cta_found = [w for w in self.CTA_WORDS if w in norm]
        if cta_found:
            score += 3
        else:
            issues.append({"error": "Sem CTA (call-to-action) no final do Sobre", "fix": "Adicione: 'Vamos conversar?' ou 'Conecte-se comigo'"})

        return {"score": min(score, 20), "issues": issues, "keyword_matches": keyword_matches}

    def _score_experience(self, experience_text: str) -> dict:
        """Scoring determinístico de Experiência (max 25 pontos)"""
        score = 0
        issues = []
        norm = normalize_text(experience_text)

        verb_matches = [v for v in self.ACTION_VERBS if v in norm]
        verb_score = min(len(verb_matches) * 1.2, 5)
        score += verb_score

        if not verb_matches:
            issues.append({"error": "Poucos verbos de ação nas experiências", "fix": "Use: Liderei, Desenvolvi, Implementei, Reduzi, Otimizei"})

        bullet_count = experience_text.count("\n•") + experience_text.count("\n-") + experience_text.count("\n*")
        if bullet_count >= 5:
            score += 4
        elif bullet_count >= 3:
            score += 2
        else:
            issues.append({"error": "Poucos bullets nas experiências", "fix": "Adicione 3-5 bullets por experiência com resultados quantificados"})

        all_keywords = [kw for terms in self.TECH_KEYWORDS.values() for kw in terms]
        keyword_matches = [kw for kw in all_keywords if kw in norm]
        kw_score = min(len(keyword_matches) * 0.6, 6)
        score += kw_score

        quantified = bool(re.search(r'\d+%|\d+x|r\$|\d+\s*(mil|milhão|bi)|\d+ projetos|\d+ clientes|\d+\s*(horas|meses|anos|minutos|semanas)|\d+.*para.*\d+', norm))
        if quantified:
            score += 6
        else:
            issues.append({"error": "Experiências sem resultados quantificados", "fix": "Adicione métricas: 'reduzi 30% do tempo', 'gerei R$X em economia'"})

        if "atual" in norm or "presente" in norm or "o momento" in norm:
            score += 4
        else:
            score += 2

        return {"score": min(score, 25), "issues": issues}

    def _score_skills(self, skills: List[str]) -> dict:
        """Scoring determinístico de Skills (max 15 pontos)"""
        score = 0
        issues = []

        if not skills:
            issues.append({"error": "Nenhuma skill listada", "fix": "Adicione pelo menos 5 skills relevantes ao cargo alvo"})
            return {"score": 0, "issues": issues}

        if len(skills) >= 10:
            score += 4
        elif len(skills) >= 5:
            score += 2
        else:
            issues.append({"error": "Poucas skills listadas", "fix": "Adicione pelo menos 10 skills relevantes"})

        all_keywords = [kw for terms in self.TECH_KEYWORDS.values() for kw in terms]
        norm_skills = [normalize_text(s) for s in skills]
        relevant_matches = [kw for kw in all_keywords if any(kw in ns for ns in norm_skills)]
        relevant_score = min(len(relevant_matches) * 0.5, 5)
        score += relevant_score

        if len(skills) <= 50:
            score += 3
        elif len(skills) > 50:
            issues.append({"error": "Muitas skills listadas (>50)", "fix": "Foque nas 30-40 mais relevantes para evitar ruído"})

        if len(skills) >= 3:
            score += 3

        return {"score": min(score, 15), "issues": issues}

    def _score_seo(self, headline: str, about: str, experience: str, skills: List[str]) -> dict:
        """Scoring determinístico de SEO (max 15 pontos)"""
        score = 0
        norm_headline = normalize_text(headline)
        norm_about = normalize_text(about)
        norm_exp = normalize_text(experience)
        all_keywords = [kw for terms in self.TECH_KEYWORDS.values() for kw in terms]

        kw_in_headline = sum(1 for kw in all_keywords if kw in norm_headline)
        if kw_in_headline >= 2:
            score += 4
        elif kw_in_headline >= 1:
            score += 2

        kw_in_about = sum(1 for kw in all_keywords if kw in norm_about)
        if kw_in_about >= 5:
            score += 4
        elif kw_in_about >= 2:
            score += 2

        kw_in_exp = sum(1 for kw in all_keywords if kw in norm_exp)
        if kw_in_exp >= 5:
            score += 4
        elif kw_in_exp >= 2:
            score += 2

        if len(skills) >= 5:
            score += 3

        return {"score": min(score, 15)}

    def _score_authority(self, experience_text: str, skills: List[str]) -> dict:
        """Scoring determinístico de Autoridade (max 10 pontos)"""
        score = 0
        norm = normalize_text(experience_text)

        if len(experience_text) > 2000:
            score += 2
        elif len(experience_text) > 1000:
            score += 1

        has_cert = any(w in norm for w in ["certificação", "certified", "certificado", "aws", "azure", "google", "scrum", "pmp"])
        if has_cert:
            score += 2

        has_leadership = any(w in norm for w in ["líder", "lider", "coordenou", "gerenciou", "gerente", "head", "diretor", "apoio à liderança"])
        if has_leadership:
            score += 2

        has_impact = bool(re.search(r'\d+%|\d+\s*(mil|milhão|pessoas|equipes)|reduzi|aumentei|otimizei|implementei', norm))
        if has_impact:
            score += 2

        # Múltiplas empresas = mais experiência
        company_count = sum(1 for w in ["empresa", "corp", "ltda", "s.a", "green", "dimeso", "movicarga", "mercado livre", "pentair", "seicom", "zf", "heller"] if w in norm)
        if company_count >= 3:
            score += 2
        elif company_count >= 1:
            score += 1

        return {"score": min(score, 10)}

    def audit(self, profile_data: dict, target_keywords: List[str] = None) -> LinkedInAudit:
        """Auditoria completa de perfil LinkedIn - 100% Python determinístico"""
        if target_keywords is None:
            target_keywords = ["dados", "bi", "python", "sql", "power bi", "analytics", "etl"]

        logger.log("[LINKEDIN OPTIMIZER] Iniciando auditoria determinística...")
        result = LinkedInAudit()

        headline = profile_data.get("headline", "")
        about = profile_data.get("about", "")
        experience = profile_data.get("experience", "")
        skills = profile_data.get("skills", [])

        h_result = self._score_headline(headline)
        result.headline_score = h_result["score"]
        result.issues.extend(h_result.get("issues", []))

        a_result = self._score_about(about)
        result.about_score = a_result["score"]
        result.issues.extend(a_result.get("issues", []))

        e_result = self._score_experience(experience)
        result.experience_score = e_result["score"]
        result.issues.extend(e_result.get("issues", []))

        s_result = self._score_skills(skills)
        result.skills_score = s_result["score"]
        result.issues.extend(s_result.get("issues", []))

        seo_result = self._score_seo(headline, about, experience, skills)
        result.seo_score = seo_result["score"]

        auth_result = self._score_authority(experience, skills)
        result.authority_score = auth_result["score"]

        result.overall_score = round(
            result.headline_score + result.about_score +
            result.experience_score + result.skills_score +
            result.seo_score + result.authority_score, 1
        )

        if result.headline_score < 12:
            result.quick_wins.append({
                "action": "Reescrever headline com formato Cargo | Especialidade | Valor",
                "impact": "high",
                "effort": "quick"
            })
        if result.about_score < 14:
            result.quick_wins.append({
                "action": "Adicionar hook + resultados quantificados no Sobre",
                "impact": "high",
                "effort": "quick"
            })
        if result.skills_score < 10:
            result.quick_wins.append({
                "action": "Adicionar 10-30 skills ATS-relevantes",
                "impact": "medium",
                "effort": "quick"
            })
        if result.seo_score < 10:
            result.quick_wins.append({
                "action": "Inserir mais keywords técnicas em todas as seções",
                "impact": "high",
                "effort": "moderate"
            })

        logger.log(f"[LINKEDIN OPTIMIZER] Score: {result.overall_score}/100")
        return result

    def to_dict(self, audit: LinkedInAudit) -> dict:
        return {
            "overall_score": audit.overall_score,
            "scores": {
                "headline": audit.headline_score,
                "about": audit.about_score,
                "experience": audit.experience_score,
                "skills": audit.skills_score,
                "seo": audit.seo_score,
                "authority": audit.authority_score,
            },
            "issues": audit.issues,
            "quick_wins": audit.quick_wins,
            "suggested_headline": audit.suggested_headline,
            "suggested_about_opening": audit.suggested_about_opening,
        }


linkedin_optimizer = LinkedInOptimizer()