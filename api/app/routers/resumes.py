# ================================================================
# JARVIS CV
# ARQUIVO: resumes.py
# DESCRIÇÃO: Rotas de currículos - Upload, CRUD, versionamento
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
import uuid
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import Optional

from app.dependencies import get_current_user, check_rate_limit
from app.models.resume import ResumeResponse, ResumeList
from app.services.resume_parser import resume_parser
from app.utils.supabase_client import supabase_client
from app.utils.logger import logger

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    title: str = Form("Meu Currículo"),
    user: dict = Depends(get_current_user),
    limits: dict = Depends(check_rate_limit),
):
    file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "txt"
    if file_type not in ("pdf", "docx", "txt"):
        raise HTTPException(status_code=400, detail="Formato suportado: PDF, DOCX ou TXT.")

    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo excede o limite de 5MB.")

    raw_text, _ = await resume_parser.parse(file_bytes, file_type)

    resume_id = str(uuid.uuid4())
    data = {
        "id": resume_id,
        "user_id": user["user_id"],
        "version_number": 1,
        "content": {"title": title, "file_type": file_type},
        "raw_text": raw_text,
        "is_active": True,
    }

    try:
        response = supabase_client.client.table("resumes").insert(data).execute()
        created = response.data[0] if response.data else data
        return ResumeResponse(
            id=created["id"],
            title=title,
            file_type=file_type,
            raw_text=raw_text,
            version_number=1,
            is_active=True,
            created_at=created.get("created_at"),
        )
    except Exception as e:
        logger.error("[RESUME UPLOAD ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao salvar currículo.")


@router.get("/", response_model=ResumeList)
async def list_resumes(user: dict = Depends(get_current_user)):
    try:
        response = (
            supabase_client.client.table("resumes")
            .select("*")
            .eq("user_id", user["user_id"])
            .order("created_at", desc=True)
            .execute()
        )
        resumes = [
            ResumeResponse(
                id=r["id"],
                title=r.get("content", {}).get("title", "Sem título"),
                file_type=r.get("content", {}).get("file_type"),
                raw_text=r.get("raw_text"),
                version_number=r.get("version_number", 1),
                is_active=r.get("is_active", True),
                created_at=r.get("created_at"),
            )
            for r in (response.data or [])
        ]
        return ResumeList(resumes=resumes, total=len(resumes))
    except Exception as e:
        logger.error("[RESUME LIST ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao listar currículos.")


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str, user: dict = Depends(get_current_user)):
    try:
        response = (
            supabase_client.client.table("resumes")
            .select("*")
            .eq("id", resume_id)
            .eq("user_id", user["user_id"])
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Currículo não encontrado.")
        r = response.data[0]
        return ResumeResponse(
            id=r["id"],
            title=r.get("content", {}).get("title", "Sem título"),
            file_type=r.get("content", {}).get("file_type"),
            raw_text=r.get("raw_text"),
            version_number=r.get("version_number", 1),
            is_active=r.get("is_active", True),
            created_at=r.get("created_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[RESUME GET ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao buscar currículo.")


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str, user: dict = Depends(get_current_user)):
    try:
        supabase_client.client.table("resumes").delete().eq("id", resume_id).eq(
            "user_id", user["user_id"]
        ).execute()
    except Exception as e:
        logger.error("[RESUME DELETE ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao excluir currículo.")
