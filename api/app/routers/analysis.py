# ================================================================
# JARVIS CV
# ARQUIVO: analysis.py
# DESCRIÇÃO: Rotas de análise ATS - Híbrida (local + IA), carta, estratégia, reescrita
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================
import uuid
import asyncio
from typing import Dict
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File

from app.dependencies import get_current_user, check_rate_limit
from app.models.analysis import (
    AnalysisRequest, AnalysisRawRequest, AnalysisResponse,
    AnalysisHybridResponse, CoverLetterRequest, WeeklyStrategyResponse,
)
from app.services.ai_engine import ai_engine
from app.services.ats_engine import ats_engine
from app.services.docx_generator import docx_generator
from app.services.extractor import extractor
from app.utils.supabase_client import supabase_client
from app.utils.logger import logger

router = APIRouter()


@router.post("/ats", response_model=AnalysisHybridResponse, status_code=status.HTTP_201_CREATED)
async def analyze_ats(
    body: AnalysisRequest,
    user: dict = Depends(get_current_user),
    limits: dict = Depends(check_rate_limit),
):
    resume_resp = (
        supabase_client.client.table("resumes")
        .select("raw_text")
        .eq("id", body.resume_id)
        .eq("user_id", user["user_id"])
        .execute()
    )
    if not resume_resp.data or not resume_resp.data[0].get("raw_text"):
        raise HTTPException(status_code=404, detail="Currículo não encontrado ou sem texto extraído.")

    job_resp = (
        supabase_client.client.table("target_jobs")
        .select("description")
        .eq("id", body.job_id)
        .eq("user_id", user["user_id"])
        .execute()
    )
    if not job_resp.data:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")

    cv_text = resume_resp.data[0]["raw_text"]
    job_text = job_resp.data[0]["description"]

    try:
        local_result = ats_engine.score(cv_text, job_text)
        local_dict = ats_engine.to_dict(local_result)

        try:
            ai_result = await ai_engine.analyze_ats(cv_text, job_text)
        except Exception as ai_err:
            logger.warn(f"[ATS] IA falhou, usando apenas local: {ai_err}")
            ai_result = {}

        combined_score = round(
            local_result.total_score * 0.4 + ai_result.get("score", local_result.total_score) * 0.6, 1
        )

        # Normalizar missing_skills
        raw_missing_skills = ai_result.get("missing_skills", [])
        normalized_missing_skills = [
            f"{ms.get('skill', 'Skill')}: {ms.get('suggestion', '')}" if isinstance(ms, dict) else ms
            for ms in raw_missing_skills
        ]

        analysis_id = str(uuid.uuid4())

        data = {
            "id": analysis_id,
            "user_id": user["user_id"],
            "resume_id": body.resume_id,
            "job_id": body.job_id,
            "score": combined_score,
            "gap_analysis": {
                "strengths": ai_result.get("strengths", []),
                "weaknesses": ai_result.get("weaknesses", []),
                "missing_skills": ai_result.get("missing_skills", local_dict.get("keywords_missing", [])),
            },
            "suggestions": {
                "rewritten_summary": ai_result.get("rewritten_summary") or ai_result.get("optimized_resume", {}).get("summary", ""),
                "suggested_headline": ai_result.get("suggested_headline") or ai_result.get("optimized_resume", {}).get("headline", ""),
                "recommendations": ai_result.get("recommendations", []),
            },
        }
        supabase_client.client.table("optimization_results").insert(data).execute()
        await supabase_client.log_usage(user["user_id"], "analysis")

        optimized = ai_result.get("optimized_resume", {})
        recruiter = ai_result.get("recruiter_recommendation", {})
        interview = ai_result.get("interview_chance", {})

        # Garantir que recommendations SEMPRE tenha conteúdo
        raw_recommendations = ai_result.get("recommendations", [])
        if not raw_recommendations:
            raw_recommendations = recruiter.get("top_3_actions", [])
        if not raw_recommendations:
            missing = local_dict.get("keywords_missing", [])
            raw_recommendations = [
                f"Adicionar keywords faltantes: {', '.join(missing[:5])}" if missing else "Currículo bem otimizado para keywords",
                "Incluir resultados quantificáveis (%, R$, tempo economizado)",
                "Reformular experiências como bullets com ação + resultado",
            ]

        top_3 = recruiter.get("top_3_actions", [])
        if not top_3:
            top_3 = raw_recommendations[:3]

        return AnalysisHybridResponse(
            id=analysis_id,
            resume_id=body.resume_id,
            job_id=body.job_id,
            ats_score=combined_score,
            local_scores=local_dict.get("local_scores", {}),
            keywords_found=local_dict.get("keywords_found", []),
            keywords_missing=local_dict.get("keywords_missing", []),
            structure_errors=local_dict.get("structure_errors", []),
            sections_detected=local_dict.get("sections_detected", []),
            seniority_detected=local_dict.get("seniority_detected", ""),
            seniority_alignment=local_dict.get("seniority_alignment", ""),
            strengths=ai_result.get("strengths", []),
            weaknesses=ai_result.get("weaknesses", []),
            missing_skills=normalized_missing_skills,
            rewritten_summary=ai_result.get("rewritten_summary") or optimized.get("summary", ""),
            suggested_headline=ai_result.get("suggested_headline") or optimized.get("headline", ""),
            recommendations=raw_recommendations,
            optimized_skills=optimized.get("skills_section", []),
            experience_highlights=optimized.get("experience_highlights", []),
            key_changes=optimized.get("key_changes", []),
            interview_chance=interview.get("percent", 0),
            interview_factors=interview.get("factors", []),
            recruiter_verdict=recruiter.get("verdict", ""),
            recruiter_summary=recruiter.get("summary", ""),
            top_3_actions=top_3,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[ATS ANALYSIS ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro na análise ATS.")


@router.post("/ats/raw", response_model=AnalysisHybridResponse, status_code=status.HTTP_201_CREATED)
async def analyze_ats_raw(body: AnalysisRawRequest):
    try:
        local_result = ats_engine.score(body.cv_text, body.job_text)
        local_dict = ats_engine.to_dict(local_result)

        try:
            ai_result = await ai_engine.analyze_ats(body.cv_text, body.job_text)
        except Exception as ai_err:
            logger.warn(f"[ATS RAW] IA falhou, usando apenas local: {ai_err}")
            ai_result = {}

        combined_score = round(
            local_result.total_score * 0.4 + ai_result.get("score", local_result.total_score) * 0.6, 1
        )

        # Normalizar missing_skills (pode vir como lista de dicts ou strings)
        raw_missing_skills = ai_result.get("missing_skills", [])
        normalized_missing_skills = [
            f"{ms.get('skill', 'Skill')}: {ms.get('suggestion', '')}" if isinstance(ms, dict) else ms
            for ms in raw_missing_skills
        ]

        optimized = ai_result.get("optimized_resume", {})
        recruiter = ai_result.get("recruiter_recommendation", {})
        interview = ai_result.get("interview_chance", {})

        # Garantir que recommendations SEMPRE tenha conteúdo
        raw_recommendations = ai_result.get("recommendations", [])
        if not raw_recommendations:
            # Fallback: usar top_3_actions do recruiter ou gerar do fallback local
            raw_recommendations = recruiter.get("top_3_actions", [])
        if not raw_recommendations:
            # Último recurso: gerar do keyword matching
            missing = local_dict.get("keywords_missing", [])
            raw_recommendations = [
                f"Adicionar keywords faltantes: {', '.join(missing[:5])}" if missing else "Currículo bem otimizado para keywords",
                "Incluir resultados quantificáveis (%, R$, tempo economizado)",
                "Reformular experiências como bullets com ação + resultado",
            ]

        # Garantir que top_3_actions SEMPRE tenha conteúdo
        top_3 = recruiter.get("top_3_actions", [])
        if not top_3:
            top_3 = raw_recommendations[:3]

        return AnalysisHybridResponse(
            id="raw-session",
            ats_score=combined_score,
            local_scores=local_dict.get("local_scores", {}),
            keywords_found=local_dict.get("keywords_found", []),
            keywords_missing=local_dict.get("keywords_missing", []),
            structure_errors=local_dict.get("structure_errors", []),
            sections_detected=local_dict.get("sections_detected", []),
            seniority_detected=local_dict.get("seniority_detected", ""),
            seniority_alignment=local_dict.get("seniority_alignment", ""),
            strengths=ai_result.get("strengths", []),
            weaknesses=ai_result.get("weaknesses", []),
            missing_skills=normalized_missing_skills,
            rewritten_summary=ai_result.get("rewritten_summary") or optimized.get("summary", ""),
            suggested_headline=ai_result.get("suggested_headline") or optimized.get("headline", ""),
            recommendations=raw_recommendations,
            optimized_skills=optimized.get("skills_section", []),
            experience_highlights=optimized.get("experience_highlights", []),
            key_changes=optimized.get("key_changes", []),
            interview_chance=interview.get("percent", 0),
            interview_factors=interview.get("factors", []),
            recruiter_verdict=recruiter.get("verdict", ""),
            recruiter_summary=recruiter.get("summary", ""),
            top_3_actions=top_3,
        )
    except Exception as e:
        logger.error("[ATS RAW ANALYSIS ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro na análise ATS.")


@router.post("/ats/raw/docx")
async def analyze_ats_raw_docx(body: AnalysisRawRequest):
    try:
        local_result = ats_engine.score(body.cv_text, body.job_text)
        local_dict = ats_engine.to_dict(local_result)

        try:
            ai_result = await ai_engine.analyze_ats(body.cv_text, body.job_text)
        except Exception:
            ai_result = {}

        optimized = ai_result.get("optimized_resume", {})
        headline = optimized.get("headline", "Currículo Otimizado")
        summary = optimized.get("summary", ai_result.get("rewritten_summary", ""))
        skills = optimized.get("skills_section", [])
        highlights = optimized.get("experience_highlights", [])
        changes = optimized.get("key_changes", [])

        filepath = await docx_generator.generate_premium_resume(
            headline=headline,
            summary=summary,
            skills=skills,
            experience_highlights=highlights,
            key_changes=changes,
        )

        from fastapi.responses import FileResponse
        return FileResponse(
            path=filepath,
            filename="Curriculo_Otimizado_JARVIS_CV.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        logger.error("[ATS RAW DOCX ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao gerar DOCX.")


@router.post("/cover-letter", response_model=AnalysisResponse)
async def generate_cover_letter(
    body: CoverLetterRequest,
    user: dict = Depends(get_current_user),
):
    plan = user.get("plan", "free")
    if plan != "elite":
        raise HTTPException(status_code=403, detail="Carta de apresentação requer plano ELITE.")

    result_resp = (
        supabase_client.client.table("optimization_results")
        .select("resume_id, job_id")
        .eq("id", body.analysis_id)
        .eq("user_id", user["user_id"])
        .execute()
    )
    if not result_resp.data:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")

    resume_id = result_resp.data[0]["resume_id"]
    job_id = result_resp.data[0]["job_id"]

    cv_resp = supabase_client.client.table("resumes").select("raw_text").eq("id", resume_id).execute()
    job_resp = supabase_client.client.table("target_jobs").select("description").eq("id", job_id).execute()

    if not cv_resp.data or not job_resp.data:
        raise HTTPException(status_code=404, detail="Dados não encontrados.")

    cover_letter = await ai_engine.generate_cover_letter(
        cv_resp.data[0]["raw_text"], job_resp.data[0]["description"], body.tone
    )

    supabase_client.client.table("optimization_results").update(
        {"suggestions": {"cover_letter": cover_letter}}
    ).eq("id", body.analysis_id).execute()

    return AnalysisResponse(id=body.analysis_id, cover_letter=cover_letter)


@router.post("/weekly-strategy", response_model=WeeklyStrategyResponse)
async def generate_weekly_strategy(user: dict = Depends(get_current_user)):
    plan = user.get("plan", "free")
    if plan != "elite":
        raise HTTPException(status_code=403, detail="Estratégia semanal requer plano ELITE.")

    resume_resp = (
        supabase_client.client.table("resumes")
        .select("raw_text")
        .eq("user_id", user["user_id"])
        .eq("is_active", True)
        .execute()
    )
    if not resume_resp.data:
        raise HTTPException(status_code=404, detail="Nenhum currículo ativo encontrado.")

    jobs_resp = (
        supabase_client.client.table("target_jobs")
        .select("title, description, company")
        .eq("user_id", user["user_id"])
        .execute()
    )

    cv_text = resume_resp.data[0]["raw_text"]
    jobs_text = "\n".join(
        [f"- {j['title']} @ {j.get('company', 'N/A')}: {j['description'][:200]}" for j in (jobs_resp.data or [])]
    )

    try:
        result = await ai_engine.generate_weekly_strategy(cv_text, jobs_text)
        strategy_id = str(uuid.uuid4())

        data = {
            "id": strategy_id,
            "user_id": user["user_id"],
            "strategy_text": result.get("strategy_text", ""),
            "target_jobs": result.get("target_jobs", []),
            "action_items": result.get("action_items", []),
        }
        supabase_client.client.table("weekly_strategies").insert(data).execute()

        return WeeklyStrategyResponse(
            id=strategy_id,
            week_start="",
            strategy_text=result.get("strategy_text", ""),
            target_jobs=result.get("target_jobs", []),
            action_items=result.get("action_items", []),
        )
    except Exception as e:
        logger.error("[WEEKLY STRATEGY ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao gerar estratégia semanal.")


@router.post("/rewrite")
async def rewrite_resume(
    body: AnalysisRequest,
    user: dict = Depends(get_current_user),
):
    plan = user.get("plan", "free")
    if plan not in ("pro", "elite"):
        raise HTTPException(status_code=403, detail="Reescrita de currículo requer plano PRO ou ELITE.")

    try:
        cv_resp = (
            supabase_client.client.table("resumes")
            .select("raw_text")
            .eq("id", body.resume_id)
            .eq("user_id", user["user_id"])
            .execute()
        )
        job_resp = (
            supabase_client.client.table("target_jobs")
            .select("description")
            .eq("id", body.job_id)
            .eq("user_id", user["user_id"])
            .execute()
        )

        if not cv_resp.data or not job_resp.data:
            raise HTTPException(status_code=404, detail="Currículo ou vaga não encontrados.")

        result = await ai_engine.rewrite_resume(cv_resp.data[0]["raw_text"], job_resp.data[0]["description"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[RESUME REWRITE ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro na reescrita do currículo.")


@router.post("/extract-cv")
async def extract_cv(file: UploadFile = File(...)):
    """Extrai texto de PDF/DOCX sem armazenar no servidor"""
    try:
        content = await file.read()
        text = extractor.extract_text_from_file(content, file.filename)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/extract-job")
async def extract_job(body: Dict[str, str]):
    """Extrai texto de uma URL de vaga"""
    url = body.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL da vaga é obrigatória.")
    try:
        text = await extractor.extract_text_from_url(url)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))