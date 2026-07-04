# ================================================================
# JARVIS CV
# ARQUIVO: jobs.py
# DESCRIÇÃO: Rotas de vagas - CRUD manual + busca em portais com scraping
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional, List

from app.dependencies import get_current_user, check_rate_limit
from app.models.job import JobSearch, JobManual, JobResponse, JobList, JobSearchRequest, JobSearchResult
from app.services.job_scraper import job_scraper
from app.utils.supabase_client import supabase_client
from app.utils.logger import logger

router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: JobManual,
    user: dict = Depends(get_current_user),
    limits: dict = Depends(check_rate_limit),
):
    job_id = str(uuid.uuid4())
    data = {
        "id": job_id,
        "user_id": user["user_id"],
        "title": body.title,
        "company": body.company,
        "description": body.description,
        "url": body.url,
        "location": body.location,
        "salary_range": body.salary_range,
        "is_remote": body.is_remote,
    }

    try:
        response = supabase_client.client.table("target_jobs").insert(data).execute()
        created = response.data[0] if response.data else data
        await supabase_client.log_usage(user["user_id"], "job")
        return JobResponse(
            id=created["id"],
            title=body.title,
            company=body.company,
            description=body.description,
            url=body.url,
            location=body.location,
            salary_range=body.salary_range,
            is_remote=body.is_remote,
            created_at=created.get("created_at"),
        )
    except Exception as e:
        logger.error("[JOB CREATE ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao criar vaga.")


@router.get("/", response_model=JobList)
async def list_jobs(user: dict = Depends(get_current_user)):
    try:
        response = (
            supabase_client.client.table("target_jobs")
            .select("*")
            .eq("user_id", user["user_id"])
            .order("created_at", desc=True)
            .execute()
        )
        jobs = [
            JobResponse(
                id=j["id"],
                title=j["title"],
                company=j.get("company"),
                description=j["description"],
                url=j.get("url"),
                source=j.get("source"),
                location=j.get("location"),
                salary_range=j.get("salary_range"),
                is_remote=j.get("is_remote", False),
                created_at=j.get("created_at"),
            )
            for j in (response.data or [])
        ]
        return JobList(jobs=jobs, total=len(jobs))
    except Exception as e:
        logger.error("[JOB LIST ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao listar vagas.")


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, user: dict = Depends(get_current_user)):
    try:
        response = (
            supabase_client.client.table("target_jobs")
            .select("*")
            .eq("id", job_id)
            .eq("user_id", user["user_id"])
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Vaga não encontrada.")
        j = response.data[0]
        return JobResponse(
            id=j["id"],
            title=j["title"],
            company=j.get("company"),
            description=j["description"],
            url=j.get("url"),
            source=j.get("source"),
            location=j.get("location"),
            salary_range=j.get("salary_range"),
            is_remote=j.get("is_remote", False),
            created_at=j.get("created_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[JOB GET ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao buscar vaga.")


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, user: dict = Depends(get_current_user)):
    try:
        supabase_client.client.table("target_jobs").delete().eq("id", job_id).eq(
            "user_id", user["user_id"]
        ).execute()
    except Exception as e:
        logger.error("[JOB DELETE ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao excluir vaga.")


@router.post("/search", response_model=JobSearchResult)
async def search_jobs(
    body: JobSearchRequest,
    user: dict = Depends(get_current_user),
    limits: dict = Depends(check_rate_limit),
):
    """Busca vagas em múltiplos portais com scraping + fit score (autenticado)"""
    plan = user.get("plan", "free")
    max_portals = 9 if plan in ("pro", "elite") else 3

    try:
        profile_keywords = body.profile_keywords or []

        if not profile_keywords:
            try:
                resume_resp = (
                    supabase_client.client.table("resumes")
                    .select("raw_text")
                    .eq("user_id", user["user_id"])
                    .eq("is_active", True)
                    .execute()
                )
                if resume_resp.data and resume_resp.data[0].get("raw_text"):
                    from app.utils.text_utils import normalize_text
                    norm = normalize_text(resume_resp.data[0]["raw_text"])
                    all_tech = []
                    from app.services.ats_engine import TECH_KEYWORDS
                    for terms in TECH_KEYWORDS.values():
                        all_tech.extend(terms)
                    profile_keywords = [t for t in all_tech if t in norm][:15]
            except Exception:
                pass

        portal_list = body.portals[:max_portals] if body.portals else None

        jobs = await job_scraper.search_all(
            query=body.query,
            location=body.location or "",
            remote=body.remote or False,
            work_mode=body.work_mode or "remote",
            radius_km=body.radius_km or 0,
            portals=portal_list,
            profile_keywords=profile_keywords,
        )

        await supabase_client.log_usage(user["user_id"], "job_search")

        return JobSearchResult(
            jobs=job_scraper.to_dict_list(jobs),
            total=len(jobs),
            query=body.query,
            portals_searched=portal_list or ["indeed", "linkedin", "catho"],
        )
    except Exception as e:
        logger.error("[JOB SEARCH ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao buscar vagas nos portais.")


@router.post("/search/raw", response_model=JobSearchResult)
async def search_jobs_raw(body: JobSearchRequest):
    """Busca vagas em múltiplos portais - sem autenticação (demo)"""
    try:
        portal_list = body.portals[:3] if body.portals else None

        jobs = await job_scraper.search_all(
            query=body.query,
            location=body.location or "",
            remote=body.remote or False,
            work_mode=body.work_mode or "remote",
            radius_km=body.radius_km or 0,
            portals=portal_list,
            profile_keywords=body.profile_keywords or [],
        )

        return JobSearchResult(
            jobs=job_scraper.to_dict_list(jobs),
            total=len(jobs),
            query=body.query,
            portals_searched=portal_list or ["indeed", "linkedin", "catho"],
        )
    except Exception as e:
        logger.error("[JOB SEARCH RAW ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao buscar vagas nos portais.")
