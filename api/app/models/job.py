# ================================================================
# JARVIS CV
# ARQUIVO: job.py
# DESCRIÇÃO: Modelos Pydantic para vagas - busca, scraping, resposta
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobSearch(BaseModel):
    query: str
    location: Optional[str] = None
    portal: Optional[str] = "indeed"


class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    portals: Optional[List[str]] = None
    remote: Optional[bool] = False
    work_mode: Optional[str] = "remote"
    radius_km: Optional[int] = 0
    profile_keywords: Optional[List[str]] = None


class JobSearchResult(BaseModel):
    jobs: List[dict] = []
    total: int = 0
    query: str = ""
    portals_searched: List[str] = []


class JobManual(BaseModel):
    title: str
    company: Optional[str] = None
    description: str
    url: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    is_remote: bool = False


class JobResponse(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    description: str
    url: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    is_remote: bool = False
    created_at: Optional[datetime] = None


class JobList(BaseModel):
    jobs: list[JobResponse]
    total: int
