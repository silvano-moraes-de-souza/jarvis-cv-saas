# ================================================================
# JARVIS CV
# ARQUIVO: analysis.py
# DESCRIÇÃO: Modelos Pydantic para análise ATS híbrida - local + IA
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    resume_id: str
    job_id: str


class AnalysisRawRequest(BaseModel):
    cv_text: str
    job_text: str


class AnalysisResponse(BaseModel):
    id: str
    resume_id: Optional[str] = None
    job_id: Optional[str] = None
    ats_score: Optional[float] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    missing_skills: List[str] = []
    rewritten_summary: Optional[str] = None
    suggested_headline: Optional[str] = None
    recommendations: List[str] = []
    cover_letter: Optional[str] = None
    optimized_resume_url: Optional[str] = None
    created_at: Optional[datetime] = None


class AnalysisHybridResponse(BaseModel):
    id: str
    resume_id: Optional[str] = None
    job_id: Optional[str] = None
    ats_score: Optional[float] = None
    local_scores: dict = {}
    keywords_found: List[str] = []
    keywords_missing: List[str] = []
    structure_errors: List[dict] = []
    sections_detected: List[str] = []
    seniority_detected: str = ""
    seniority_alignment: str = ""
    strengths: List[str] = []
    weaknesses: List[str] = []
    missing_skills: List[Any] = []
    rewritten_summary: Optional[str] = None
    suggested_headline: Optional[str] = None
    recommendations: List[str] = []
    optimized_skills: List[str] = []
    experience_highlights: List[str] = []
    key_changes: List[dict] = []
    interview_chance: Optional[float] = None
    interview_factors: List[dict] = []
    recruiter_verdict: str = ""
    recruiter_summary: str = ""
    top_3_actions: List[str] = []


class CoverLetterRequest(BaseModel):
    analysis_id: str
    tone: Optional[str] = "profissional"


class WeeklyStrategyResponse(BaseModel):
    id: str
    week_start: str
    strategy_text: str
    target_jobs: List[dict] = []
    action_items: List[str] = []
