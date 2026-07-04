# ================================================================
# JARVIS CV
# ARQUIVO: job_scraper.py
# DESCRIÇÃO: Engine de Vagas - Scraping modular 9 portais + score fit
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================
import httpx
import asyncio
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from datetime import datetime

from app.config import settings
from app.utils.logger import logger
from app.utils.text_utils import normalize_text


@dataclass
class JobMatch:
    title: str = ""
    company: str = ""
    location: str = ""
    salary_range: str = ""
    is_remote: bool = False
    url: str = ""
    source: str = ""
    description: str = ""
    fit_score: float = 0.0
    application_difficulty: str = "moderate"
    required_keywords: List[str] = field(default_factory=list)
    attack_priority: int = 5
    posted_date: str = ""


PORTAL_CONFIGS = {
    "indeed": {
        "search_url": "https://br.indeed.com/jobs",
        "selectors": {
            "job_card": ".job_seen_beacon, .jobsearch-ResultsList > li",
            "title": ".jobTitle a, h2 a",
            "company": ".companyName, [data-testid='company-name']",
            "location": ".companyLocation, [data-testid='text-location']",
            "salary": ".salary-snippet, [data-testid='attribute_snippet_testid']",
            "description": ".job-snippet",
            "link": ".jobTitle a",
        },
    },
    "catho": {
        "search_url": "https://www.catho.com.br/vagas",
        "selectors": {
            "job_card": "[data-testid='job-card'], .job-card",
            "title": "h2 a, [data-testid='job-title']",
            "company": "[data-testid='company-name'], .company-name",
            "location": "[data-testid='job-location'], .location",
            "salary": "[data-testid='salary'], .salary",
            "description": ".job-description, [data-testid='job-description']",
            "link": "h2 a",
        },
    },
    "linkedin": {
        "search_url": "https://www.linkedin.com/jobs/search",
        "selectors": {
            "job_card": ".jobs-search__results-list li, .job-search-card",
            "title": ".base-search-card__title, h3",
            "company": ".base-search-card__subtitle, h4",
            "location": ".job-search-card__location",
            "salary": ".job-search-card__salary-info",
            "description": ".job-search-card__snippet",
            "link": "a.base-card__full-link",
        },
    },
    "gupy": {
        "search_url": "https://portal.gupy.io/search",
        "selectors": {
            "job_card": "[data-testid='job-card'], .job-card",
            "title": "h2, [data-testid='job-title']",
            "company": ".company-name",
            "location": ".location",
            "salary": ".salary",
            "description": ".job-description",
            "link": "a[href*='/job/']",
        },
    },
    "remotar": {
        "search_url": "https://remotar.com.br/vagas",
        "selectors": {
            "job_card": ".job-card, .vaga-card",
            "title": "h2 a, .job-title",
            "company": ".company-name",
            "location": ".location, .remote-badge",
            "salary": ".salary",
            "description": ".job-description",
            "link": "h2 a",
        },
    },
    "geekhunter": {
        "search_url": "https://www.geekhunter.com.br/vagas",
        "selectors": {
            "job_card": ".job-card, .vaga-item",
            "title": "h2 a, .job-title",
            "company": ".company-name",
            "location": ".location",
            "salary": ".salary",
            "description": ".job-description",
            "link": "h2 a",
        },
    },
    "programathor": {
        "search_url": "https://programathor.com.br/jobs",
        "selectors": {
            "job_card": ".job-card, .job-list-item",
            "title": "h2 a, .job-title",
            "company": ".company-name",
            "location": ".location",
            "salary": ".salary",
            "description": ".job-description",
            "link": "h2 a",
        },
    },
    "nerdin": {
        "search_url": "https://nerdin.com.br/vagas",
        "selectors": {
            "job_card": ".job-card, .vaga-card",
            "title": "h2 a, .job-title",
            "company": ".company-name",
            "location": ".location",
            "salary": ".salary",
            "description": ".job-description",
            "link": "h2 a",
        },
    },
    "infojobs": {
        "search_url": "https://www.infojobs.com.br/vagas",
        "selectors": {
            "job_card": ".vaga-card, .job-card",
            "title": "h2 a, .job-title",
            "company": ".company-name",
            "location": ".location",
            "salary": ".salary",
            "description": ".job-description",
            "link": "h2 a",
        },
    },
}

SEARCH_TERMS_MAP = {
    "analista dados": ["analista+de+dados", "data+analyst", "analista+bi"],
    "bi": ["business+intelligence", "analista+bi", "bi+analyst"],
    "python": ["python+developer", "desenvolvedor+python", "python+analista"],
    "power bi": ["power+bi", "analista+power+bi", "powerbi"],
    "sql": ["sql+analyst", "analista+sql", "sql+developer"],
}


class JobScraper:
    """Engine de Vagas - Scraping modular com 9 portais"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _build_search_url(self, portal: str, query: str, location: str = "", remote: bool = False, work_mode: str = "remote", radius_km: int = 0) -> str:
        config = PORTAL_CONFIGS.get(portal, {})
        base = config.get("search_url", "")

        encoded_query = query.replace(" ", "+")
        is_hybrid = work_mode == "hybrid"
        is_onsite = work_mode == "onsite"

        if portal == "indeed":
            url = f"{base}?q={encoded_query}"
            if location:
                url += f"&l={location.replace(' ', '+')}"
            if radius_km > 0:
                url += f"&radius={radius_km}"
            if remote or work_mode == "remote":
                url += "&sc=0kf%3AATTR%28remote%29%3B"
            elif is_hybrid:
                url += "&sc=0kf%3AATTR%28hybrid%29%3B"
            return url
        elif portal == "linkedin":
            url = f"{base}?keywords={encoded_query}"
            if location:
                url += f"&location={location.replace(' ', '+')}"
            if remote or work_mode == "remote":
                url += "&f_WRA=true"
            elif is_hybrid:
                url += "&f_WHB=true"
            elif is_onsite:
                url += "&f_WHB=false&f_WRA=false"
            if radius_km > 0 and location:
                url += f"&distance={radius_km}"
            return url
        elif portal == "catho":
            modo = "remotework=true" if (remote or work_mode == "remote") else "remotework=true&hybrid=true" if is_hybrid else "remotework=false"
            return f"{base}?q={encoded_query}&{modo}"
        else:
            url = f"{base}?q={encoded_query}"
            if remote or work_mode == "remote":
                url += "&remote=true"
            elif is_hybrid:
                url += "&hybrid=true"
            return url

    def _parse_portal(self, html: str, portal: str) -> List[JobMatch]:
        config = PORTAL_CONFIGS.get(portal, {})
        selectors = config.get("selectors", {})
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        cards = soup.select(selectors.get("job_card", "div"))
        for card in cards[:20]:
            try:
                title_el = card.select_one(selectors.get("title", ""))
                company_el = card.select_one(selectors.get("company", ""))
                location_el = card.select_one(selectors.get("location", ""))
                salary_el = card.select_one(selectors.get("salary", ""))
                desc_el = card.select_one(selectors.get("description", ""))
                link_el = card.select_one(selectors.get("link", ""))

                title = title_el.get_text(strip=True) if title_el else ""
                if not title or len(title) < 3:
                    continue

                url = ""
                if link_el and link_el.get("href"):
                    href = link_el.get("href", "")
                    url = href if href.startswith("http") else f"https://{portal}.com{href}"

                job = JobMatch(
                    title=title,
                    company=company_el.get_text(strip=True) if company_el else "",
                    location=location_el.get_text(strip=True) if location_el else "",
                    salary_range=salary_el.get_text(strip=True) if salary_el else "",
                    url=url,
                    source=portal,
                    description=desc_el.get_text(strip=True)[:500] if desc_el else "",
                    is_remote="remote" in (location_el.get_text(strip=True).lower() if location_el else ""),
                )
                jobs.append(job)
            except Exception as e:
                logger.warn(f"[SCRAPER] Erro ao parsear card {portal}: {e}")
                continue

        return jobs

    def _calculate_fit_score(self, job: JobMatch, profile_keywords: List[str]) -> float:
        if not profile_keywords:
            return 50.0

        job_text = normalize_text(f"{job.title} {job.description} {job.company}")
        matches = sum(1 for kw in profile_keywords if normalize_text(kw) in job_text)
        base_score = (matches / len(profile_keywords)) * 100

        title_boost = 0
        high_value = ["senior", "sênior", "lead", "pleno", "analista", "dados", "bi", "python"]
        for hv in high_value:
            if hv in job_text:
                title_boost += 5

        remote_boost = 15 if job.is_remote else 0

        score = min(base_score + title_boost + remote_boost, 100)
        job.fit_score = round(score, 1)

        if score >= 75:
            job.attack_priority = 9
            job.application_difficulty = "moderate"
        elif score >= 50:
            job.attack_priority = 7
            job.application_difficulty = "moderate"
        elif score >= 30:
            job.attack_priority = 5
            job.application_difficulty = "hard"
        else:
            job.attack_priority = 3
            job.application_difficulty = "very_hard"

        return score

    async def search_portal(self, portal: str, query: str, location: str = "", remote: bool = False, work_mode: str = "remote", radius_km: int = 0) -> List[JobMatch]:
        url = self._build_search_url(portal, query, location, remote, work_mode, radius_km)
        logger.log(f"[SCRAPER] Buscando {portal}: {url}")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

            return self._parse_portal(response.text, portal)
        except Exception as e:
            logger.warn(f"[SCRAPER] Erro {portal}: {e}")
            return []

    async def search_all(
        self,
        query: str,
        location: str = "",
        remote: bool = False,
        work_mode: str = "remote",
        radius_km: int = 0,
        portals: List[str] = None,
        profile_keywords: List[str] = None,
    ) -> List[JobMatch]:
        if portals is None:
            portals = [p for p, c in settings.job_portals.items() if c.get("enabled", True)]

        search_terms = SEARCH_TERMS_MAP.get(query.lower(), [query.replace(" ", "+")])
        all_jobs: List[JobMatch] = []

        for term in search_terms:
            tasks = [self.search_portal(portal, term, location, remote, work_mode, radius_km) for portal in portals]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_jobs.extend(result)

        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job.title}|{job.company}|{job.source}"
            if key not in seen and job.title:
                seen.add(key)
                unique_jobs.append(job)

        if profile_keywords:
            for job in unique_jobs:
                self._calculate_fit_score(job, profile_keywords)

        unique_jobs.sort(key=lambda j: j.fit_score, reverse=True)

        logger.log(f"[SCRAPER] {len(unique_jobs)} vagas únicas de {len(portals)} portais")
        return unique_jobs[:50]

    def to_dict_list(self, jobs: List[JobMatch]) -> List[dict]:
        return [
            {
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "salary_range": j.salary_range,
                "is_remote": j.is_remote,
                "url": j.url,
                "source": j.source,
                "description": j.description[:300],
                "fit_score": j.fit_score,
                "application_difficulty": j.application_difficulty,
                "required_keywords": j.required_keywords,
                "attack_priority": j.attack_priority,
            }
            for j in jobs
        ]


job_scraper = JobScraper()
