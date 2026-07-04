# ================================================================
# JARVIS CV
# ARQUIVO: documents.py
# DESCRIÇÃO: Rotas de documentos - Geração DOCX premium ATS-friendly
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

from app.dependencies import get_current_user
from app.services.docx_generator import docx_generator
from app.utils.supabase_client import supabase_client
from app.utils.logger import logger

router = APIRouter()


class DocxGenerateRequest(BaseModel):
    headline: str = "Currículo Otimizado"
    summary: str = ""
    skills: List[str] = []
    experience_highlights: List[str] = []
    key_changes: List[dict] = []
    contact_info: Optional[dict] = None
    original_name: str = "Curriculo_Otimizado"


@router.get("/{analysis_id}/docx")
async def download_optimized_docx(
    analysis_id: str,
    user: dict = Depends(get_current_user),
):
    plan = user.get("plan", "free")
    if plan not in ("pro", "elite"):
        raise HTTPException(status_code=403, detail="Download DOCX requer plano PRO ou ELITE.")

    try:
        result_resp = (
            supabase_client.client.table("optimization_results")
            .select("*")
            .eq("id", analysis_id)
            .eq("user_id", user["user_id"])
            .execute()
        )
        if not result_resp.data:
            raise HTTPException(status_code=404, detail="Análise não encontrada.")

        result = result_resp.data[0]
        suggestions = result.get("suggestions", {})
        gap = result.get("gap_analysis", {})

        filepath = await docx_generator.generate_premium_resume(
            headline=suggestions.get("suggested_headline", "Currículo Otimizado JARVIS CV"),
            summary=suggestions.get("rewritten_summary", ""),
            skills=gap.get("strengths", []),
            experience_highlights=suggestions.get("recommendations", []),
        )

        return FileResponse(
            path=filepath,
            filename="Curriculo_Otimizado_JARVIS_CV.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[DOCX DOWNLOAD ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao gerar documento DOCX.")


@router.post("/generate")
async def generate_docx_raw(body: DocxGenerateRequest):
    try:
        filepath = await docx_generator.generate_premium_resume(
            headline=body.headline,
            summary=body.summary,
            skills=body.skills,
            experience_highlights=body.experience_highlights,
            key_changes=body.key_changes,
            contact_info=body.contact_info,
            original_name=body.original_name,
        )

        filename = f"{body.original_name}_JARVIS_CV.docx"
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        logger.error("[DOCX GENERATE ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao gerar documento DOCX.")
