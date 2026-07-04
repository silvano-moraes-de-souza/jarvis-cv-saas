# ================================================================
# JARVIS CV
# ARQUIVO: linkedin.py
# DESCRIÇÃO: Rotas de auditoria LinkedIn - Score + IA
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 5.0.0
# ================================================================
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from app.dependencies import get_current_user
from app.services.linkedin_optimizer import linkedin_optimizer
from app.services.ai_engine import ai_engine
from app.utils.logger import logger

router = APIRouter()


class LinkedInAuditRequest(BaseModel):
    profile_url: str = ""
    headline: str = ""
    about: str = ""
    experience: str = ""
    skills: List[str] = []
    target_keywords: Optional[List[str]] = None


class LinkedInAuditResponse(BaseModel):
    overall_score: float = 0.0
    scores: dict = {}
    issues: List[dict] = []
    quick_wins: List[dict] = []
    ai_audit: dict = {}


@router.post("/audit", response_model=LinkedInAuditResponse)
async def audit_linkedin(
    body: LinkedInAuditRequest,
    user: dict = Depends(get_current_user),
):
    plan = user.get("plan", "free")
    if plan != "elite":
        raise HTTPException(status_code=403, detail="Auditoria LinkedIn requer plano ELITE.")

    try:
        profile_data = {
            "headline": body.headline,
            "about": body.about,
            "experience": body.experience,
            "skills": body.skills,
        }

        local_audit = linkedin_optimizer.audit(
            profile_data=profile_data,
            target_keywords=body.target_keywords or [],
        )

        ai_audit = {}
        try:
            full_profile = f"HEADLINE: {body.headline}\n\nSOBRE: {body.about}\n\nEXPERIÊNCIA: {body.experience}\n\nSKILLS: {', '.join(body.skills)}"
            ai_audit = await ai_engine.audit_linkedin(full_profile)
        except Exception as ai_err:
            logger.warn(f"[LINKEDIN] IA falhou, usando apenas local: {ai_err}")

        return LinkedInAuditResponse(
            overall_score=local_audit.overall_score,
            scores=linkedin_optimizer.to_dict(local_audit).get("scores", {}),
            issues=local_audit.issues,
            quick_wins=local_audit.quick_wins,
            ai_audit=ai_audit,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[LINKEDIN AUDIT ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro na auditoria LinkedIn.")


@router.post("/audit/raw")
async def audit_linkedin_raw(body: LinkedInAuditRequest):
    """Endpoint público para auditoria - recebe dados extraídos pelo browser do usuário."""
    try:
        headline = body.headline
        about = body.about
        experience = body.experience
        skills_list = body.skills

        profile_data = {
            "headline": headline,
            "about": about,
            "experience": experience,
            "skills": skills_list,
        }

        local_audit = linkedin_optimizer.audit(
            profile_data=profile_data,
            target_keywords=body.target_keywords or [],
        )

        ai_audit = {}
        try:
            full_profile = f"HEADLINE: {headline}\n\nSOBRE: {about}\n\nEXPERIÊNCIA: {experience}\n\nSKILLS: {', '.join(skills_list)}"
            ai_audit = await ai_engine.audit_linkedin(full_profile)
        except Exception:
            pass

        result = linkedin_optimizer.to_dict(local_audit)
        result["ai_audit"] = ai_audit
        return result
    except Exception as e:
        logger.error("[LINKEDIN RAW AUDIT ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro na auditoria LinkedIn.")
