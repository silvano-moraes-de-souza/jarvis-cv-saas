# ================================================================
# JARVIS CV
# ARQUIVO: ats_engine.py
# DESCRIÇÃO: Motor ATS Local - Scoring determinístico que simula Gupy/Catho/LinkedIn
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 4.0.0
# ================================================================
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

from app.config import settings
from app.utils.logger import logger
from app.utils.text_utils import normalize_text

# Tradução PT→EN para keywords técnicas (bidirecional)
KEYWORD_TRANSLATIONS = {
    # PT → EN
    "banco de dados": ["database", "sql"],
    "aprendizado de maquina": ["machine learning", "ml"],
    "aprendizado de máquina": ["machine learning", "ml"],
    "ciencia de dados": ["data science"],
    "ciência de dados": ["data science"],
    "engenheiro de dados": ["data engineer"],
    "analista de dados": ["data analyst"],
    "engenharia de dados": ["data engineering"],
    "armazem de dados": ["data warehouse"],
    "armazém de dados": ["data warehouse"],
    "lago de dados": ["data lake"],
    "aprendizado profundo": ["deep learning"],
    "processamento de linguagem natural": ["nlp", "natural language processing"],
    "visao computacional": ["computer vision"],
    "visão computacional": ["computer vision"],
    "nuvem": ["cloud", "aws", "gcp", "azure"],
    "contentor": ["container", "docker"],
    "orquestacao": ["orchestration", "airflow"],
    "orquestração": ["orchestration", "airflow"],
    "automacao": ["automation"],
    "automação": ["automation"],
    "integracao": ["integration", "api"],
    "integração": ["integration", "api"],
    "desenvolvimento": ["development", "developer"],
    "programacao": ["programming", "software"],
    "programação": ["programming", "software"],
    "frontend": ["frontend", "react", "angular", "vue"],
    "retaguarda": ["backend", "node", "api"],
    "fullstack": ["fullstack", "full stack"],
    "full stack": ["fullstack", "full stack"],
    "controle de versao": ["git", "version control"],
    "controle de versão": ["git", "version control"],
    "teste": ["testing", "unit test", "tdd"],
    "testes": ["testing", "unit test", "tdd"],
    "implantacao": ["deployment", "ci/cd", "cd"],
    "implantação": ["deployment", "ci/cd", "cd"],
    "monitoramento": ["monitoring", "observability"],
    "escalabilidade": ["scalability", "scalable"],
    "performance": ["performance", "optimization"],
    "otimizacao": ["optimization", "performance"],
    "otimização": ["optimization", "performance"],
    "governanca": ["governance"],
    "governança": ["governance"],
    "qualidade de dados": ["data quality"],
    "modelagem de dados": ["data modeling"],
    "pipeline de dados": ["data pipeline", "etl"],
    "tabela dinamica": ["pivot table"],
    "tabela dinâmica": ["pivot table"],
    "planilha": ["spreadsheet", "excel"],
    "estatistica": ["statistics"],
    "estatística": ["statistics"],
    "regressao": ["regression"],
    "regressão": ["regression"],
    "classificacao": ["classification"],
    "classificação": ["classification"],
    "clusterizacao": ["clustering"],
    "minerao de dados": ["data mining"],
    "mineração de dados": ["data mining"],
    "big data": ["big data", "spark", "hadoop"],
    "dados estruturados": ["structured data"],
    "dados nao estruturados": ["unstructured data"],
    "dados não estruturados": ["unstructured data"],
    "agil": ["agile", "scrum", "kanban"],
    "ágil": ["agile", "scrum", "kanban"],
    "metodologia agil": ["agile methodology", "scrum"],
    "metodologia ágil": ["agile methodology", "scrum"],
    "gestao de projetos": ["project management"],
    "gestão de projetos": ["project management"],
    "lideranca": ["leadership", "lead"],
    "liderança": ["leadership", "lead"],
    "comunicacao": ["communication"],
    "comunicação": ["communication"],
    "resolucao de problemas": ["problem solving"],
    "resolução de problemas": ["problem solving"],
    "pensamento critico": ["critical thinking"],
    "pensamento crítico": ["critical thinking"],
    "trabalho em equipe": ["teamwork", "team player"],
    "proativo": ["proactive"],
    "analise de requisitos": ["requirements analysis"],
    "análise de requisitos": ["requirements analysis"],
    "arquitetura de software": ["software architecture"],
    "microsservicos": ["microservices"],
    "microsserviços": ["microservices"],
    "api rest": ["rest api", "restful"],
    "api restful": ["rest api", "restful"],
    "graphql": ["graphql"],
    "banco de dados relacional": ["relational database", "rdbms"],
    "banco de dados nao relacional": ["nosql", "non-relational database"],
    "banco de dados não relacional": ["nosql", "non-relational database"],
}


@dataclass
class ATSResult:
    keyword_match_score: float = 0.0
    skill_density_score: float = 0.0
    structure_score: float = 0.0
    seniority_score: float = 0.0
    experience_relevance_score: float = 0.0
    format_score: float = 0.0
    total_score: float = 0.0
    keywords_found: List[str] = field(default_factory=list)
    keywords_missing: List[str] = field(default_factory=list)
    structure_errors: List[dict] = field(default_factory=list)
    sections_detected: List[str] = field(default_factory=list)
    seniority_detected: str = ""
    seniority_alignment: str = ""


ATS_SECTIONS = {
    "resumo": ["resumo", "summary", "perfil profissional", "about", "sobre"],
    "experiencia": ["experiência", "experience", "histórico profissional", "trajetória"],
    "educacao": ["educação", "education", "formação", "academic", "graduação"],
    "skills": ["skills", "habilidades", "competências", "tecnologias", "conhecimentos"],
    "certificacoes": ["certificações", "certifications", "cursos", "certificados"],
    "idiomas": ["idiomas", "languages", "fluência", "inglês"],
}

SENIORITY_PATTERNS = {
    "estagiario": ["estagiário", "intern", "trainee", "aprendiz"],
    "junior": ["junior", "júnior", "jr", "analista jr", "desenvolvedor jr"],
    "pleno": ["pleno", "pl", "mid", "mid-level", "analista", "desenvolvedor", "analista pleno"],
    "senior": ["senior", "sênior", "sr", "lead", "especialista", "analista sr"],
    "gestao": ["gerente", "manager", "diretor", "director", "head", "vp", "c-level", "coordenador", "supervisor"],
}

TECH_KEYWORDS = {
    "data": ["python", "sql", "power bi", "bi", "etl", "dw", "data warehouse", "data lake",
             "pandas", "spark", "airflow", "dbt", "tableau", "looker", "metabase",
             "analytics", "machine learning", "ml", "estatística", "r", "jupyter",
             "bigquery", "redshift", "snowflake", "databricks"],
    "eng": ["react", "node", "typescript", "javascript", "java", "go", "rust",
            "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "git",
            "api", "rest", "graphql", "microservices", "terraform"],
    "product": ["scrum", "kanban", "jira", "product", "roadmap", "okr", "kpi",
                "stakeholder", "backlog", "sprint", "agile", "lean"],
}


class ATSEngine:
    """Motor ATS Local - Scoring determinístico híbrido"""

    def _extract_keywords(self, job_text: str) -> List[str]:
        norm = normalize_text(job_text)
        keywords = []
        for category, terms in TECH_KEYWORDS.items():
            for term in terms:
                if term in norm:
                    keywords.append(term)
        tokens = norm.split()
        freq = {}
        for t in tokens:
            if len(t) >= 4:
                freq[t] = freq.get(t, 0) + 1
        for token, count in sorted(freq.items(), key=lambda x: -x[1])[:20]:
            if token not in keywords:
                keywords.append(token)
        return keywords

    def _detect_sections(self, cv_text: str) -> List[str]:
        norm = normalize_text(cv_text)
        lines = norm.split('\n')
        detected = []

        # Estratégia 1: procurar padrões em linhas curtas (headers puros)
        for line in lines:
            line_stripped = line.strip()
            if len(line_stripped) < 50:
                for section, patterns in ATS_SECTIONS.items():
                    if any(p in line_stripped for p in patterns):
                        if section not in detected:
                            detected.append(section)

        # Estratégia 2: buscar padrões no texto completo (caso não tenha headers claros)
        for section, patterns in ATS_SECTIONS.items():
            if section not in detected:
                for pattern in patterns:
                    if pattern in norm:
                        detected.append(section)
                        break

        # Estratégia 3: detectar por estrutura implícita
        # Seção de experiência: linhas com empresas + cargos + datas
        if "experiencia" not in detected:
            exp_signals = sum(1 for line in lines if any(w in line for w in ['experiência', 'experience', 'cargo', 'empresa', 'company', 'role']))
            if exp_signals >= 1:
                detected.append("experiencia")

        # Seção de skills: listas de tecnologias
        if "skills" not in detected:
            tech_count = sum(1 for t in ['python', 'sql', 'java', 'react', 'docker', 'aws', 'excel', 'power bi', 'scrum'] if t in norm)
            if tech_count >= 3:
                detected.append("skills")

        # Seção de educação: formação acadêmica
        if "educacao" not in detected:
            edu_signals = sum(1 for line in lines if any(w in line for w in ['bacharel', 'licenciatura', 'mestrado', 'doutorado', 'universidade', 'faculdade', 'graduação', 'graduation', 'degree', 'bachelor']))
            if edu_signals >= 1:
                detected.append("educacao")

        # Seção de resumo/sobre: parágrafo introdutório
        if "resumo" not in detected:
            first_lines = [l.strip() for l in lines[:10] if len(l.strip()) > 30]
            if first_lines and len(first_lines[0]) < 200:
                has_name_or_title = any(w in first_lines[0].lower() for w in ['silvano', 'cv', 'curriculo', 'resume', 'profil', 'dados', 'engenheiro', 'analista', 'desenvolvedor'])
                if has_name_or_title:
                    detected.append("resumo")

        return detected

    def _detect_seniority(self, cv_text: str) -> str:
        norm = normalize_text(cv_text)
        scores = {}
        for level, patterns in SENIORITY_PATTERNS.items():
            score = sum(1 for p in patterns if p in norm)
            if score > 0:
                scores[level] = score

        if not scores:
            return "pleno"

        return max(scores, key=scores.get)

    def _detect_job_seniority(self, job_text: str) -> str:
        norm = normalize_text(job_text)
        for level in ["gestao", "senior", "pleno", "junior", "estagiario"]:
            for pattern in SENIORITY_PATTERNS[level]:
                if pattern in norm:
                    return level
        return "pleno"

    def _check_format_issues(self, cv_text: str) -> List[dict]:
        errors = []
        if len(cv_text) < 200:
            errors.append({"error": "Currículo muito curto (mínimo 200 caracteres)", "severity": "high", "fix": "Adicione mais detalhes sobre suas experiências e habilidades"})
        if len(cv_text) > 8000:
            errors.append({"error": "Currículo muito longo (máximo 8000 caracteres)", "severity": "medium", "fix": "Reduza para 1-2 páginas. ATS truncam textos longos"})
        if cv_text.count('\n') < 5:
            errors.append({"error": "Poucas quebras de linha - formato pode não ser parseável", "severity": "high", "fix": "Use quebras de linha entre seções e itens"})
        has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text))
        if not has_email:
            errors.append({"error": "Email não encontrado", "severity": "high", "fix": "Adicione email profissional no topo"})
        has_phone = bool(re.search(r'(\+?\d{2}?\s?)?\(?\d{2}\)?\s?\d{4,5}-?\d{4}', cv_text))
        if not has_phone:
            errors.append({"error": "Telefone não encontrado", "severity": "medium", "fix": "Adicione telefone com DDD"})
        return errors

    def _keyword_matches_cv(self, keyword: str, cv_norm: str) -> bool:
        """Verifica se keyword existe no CV, incluindo traducoes PT<->EN."""
        if keyword in cv_norm:
            return True
        # Verificar se traducao existe no CV
        for pt_term, en_terms in KEYWORD_TRANSLATIONS.items():
            if keyword in en_terms and pt_term in cv_norm:
                return True
            if keyword == pt_term:
                for en in en_terms:
                    if en in cv_norm:
                        return True
        return False

    def score(self, cv_text: str, job_text: str) -> ATSResult:
        """Scoring ATS completo - 6 dimensões com pesos reais"""
        logger.log("[ATS ENGINE] Iniciando scoring determinístico...")

        result = ATSResult()
        weights = settings.ats_weights

        # 1. KEYWORD MATCH (30%)
        job_keywords = self._extract_keywords(job_text)
        cv_norm = normalize_text(cv_text)
        found = [kw for kw in job_keywords if self._keyword_matches_cv(kw, cv_norm)]

        # Missing: deduplicate and prioritize (remove translation duplicates)
        raw_missing = [kw for kw in job_keywords if kw not in found]
        seen_normalized = set()
        missing = []
        for kw in raw_missing:
            norm_kw = normalize_text(kw)
            if norm_kw not in seen_normalized:
                seen_normalized.add(norm_kw)
                missing.append(kw)

        # Prioritize: TECH_KEYWORDS terms first, then frequency-based terms
        tech_missing = [k for k in missing if any(k in t for terms in TECH_KEYWORDS.values() for t in terms)]
        other_missing = [k for k in missing if k not in tech_missing]
        missing = tech_missing[:10] + other_missing[:5]

        keyword_score = (len(found) / len(job_keywords) * 100) if job_keywords else 0
        result.keyword_match_score = min(keyword_score, 100)
        result.keywords_found = found
        result.keywords_missing = missing

        # 2. SKILL DENSITY (20%)
        all_tech = []
        for terms in TECH_KEYWORDS.values():
            all_tech.extend(terms)
        cv_skills = [t for t in all_tech if t in cv_norm]
        total_words = len(cv_norm.split())
        density = (len(cv_skills) / max(total_words, 1)) * 100
        result.skill_density_score = min(density * 10, 100)

        # 3. STRUCTURE QUALITY (15%)
        sections = self._detect_sections(cv_text)
        result.sections_detected = sections
        essential = ["resumo", "experiencia", "educacao", "skills"]
        found_essential = sum(1 for s in essential if s in sections)
        result.structure_score = (found_essential / len(essential)) * 100

        structure_errors = self._check_format_issues(cv_text)
        missing_sections = [s for s in essential if s not in sections]
        for s in missing_sections:
            structure_errors.append({
                "error": f"Seção '{s}' não detectada",
                "severity": "high",
                "fix": f"Adicione uma seção de {s} ao currículo"
            })
        result.structure_errors = structure_errors
        result.structure_score = max(0, result.structure_score - (len(structure_errors) * 5))

        # 4. SENIORITY ALIGNMENT (15%)
        cv_level = self._detect_seniority(cv_text)
        job_level = self._detect_job_seniority(job_text)
        result.seniority_detected = cv_level
        hierarchy = {"estagiario": 0, "junior": 1, "pleno": 2, "senior": 3, "gestao": 4}

        if cv_level == job_level:
            result.seniority_score = 100
            result.seniority_alignment = "match"
        elif abs(hierarchy.get(cv_level, 2) - hierarchy.get(job_level, 2)) == 1:
            result.seniority_score = 70
            result.seniority_alignment = "underqualified" if hierarchy.get(cv_level, 2) < hierarchy.get(job_level, 2) else "overqualified"
        else:
            result.seniority_score = 30
            result.seniority_alignment = "underqualified" if hierarchy.get(cv_level, 2) < hierarchy.get(job_level, 2) else "overqualified"

        # 5. EXPERIENCE RELEVANCE (10%)
        job_norm = normalize_text(job_text)
        cv_lines = cv_norm.split('\n')
        relevant_lines = 0
        for line in cv_lines:
            words = line.split()
            overlap = sum(1 for w in words if w in job_norm and len(w) >= 4)
            if overlap >= 2:
                relevant_lines += 1
        result.experience_relevance_score = min((relevant_lines / max(len(cv_lines), 1)) * 100 * 3, 100)

        # 6. FORMAT ATS COMPATIBILITY (10%)
        format_score = 100
        if cv_text.count('\t') > 10:
            format_score -= 20
        if cv_text.count('|') > 5:
            format_score -= 10
        if len(re.findall(r'[^\x00-\x7F]', cv_text)) > len(cv_text) * 0.3:
            format_score -= 5
        result.format_score = max(0, format_score)

        # TOTAL PONDERADO
        result.total_score = (
            result.keyword_match_score * weights["keyword_match"] +
            result.skill_density_score * weights["skill_density"] +
            result.structure_score * weights["structure_quality"] +
            result.seniority_score * weights["seniority_alignment"] +
            result.experience_relevance_score * weights["experience_relevance"] +
            result.format_score * weights["format_ats_compatibility"]
        )

        result.total_score = round(min(max(result.total_score, 0), 100), 1)
        logger.log(f"[ATS ENGINE] Score: {result.total_score}% | Keywords: {len(found)}/{len(job_keywords)} | Sections: {len(sections)}/{len(essential)}")
        return result

    def to_dict(self, result: ATSResult) -> dict:
        """Converte ATSResult para dict compatível com API"""
        return {
            "score": result.total_score,
            "local_scores": {
                "keyword_match": round(result.keyword_match_score, 1),
                "skill_density": round(result.skill_density_score, 1),
                "structure": round(result.structure_score, 1),
                "seniority": round(result.seniority_score, 1),
                "experience_relevance": round(result.experience_relevance_score, 1),
                "format": round(result.format_score, 1),
            },
            "keywords_found": result.keywords_found,
            "keywords_missing": result.keywords_missing,
            "structure_errors": result.structure_errors,
            "sections_detected": result.sections_detected,
            "seniority_detected": result.seniority_detected,
            "seniority_alignment": result.seniority_alignment,
        }


ats_engine = ATSEngine()
