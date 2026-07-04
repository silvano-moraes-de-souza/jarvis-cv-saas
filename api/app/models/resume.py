# ================================================================
# JARVIS CV
# ARQUIVO: resume.py
# DESCRIÇÃO: Modelos Pydantic para currículo - upload, resposta, parse
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResumeUpload(BaseModel):
    title: str = "Meu Currículo"


class ResumeResponse(BaseModel):
    id: str
    title: str
    file_type: Optional[str] = None
    file_url: Optional[str] = None
    raw_text: Optional[str] = None
    version_number: int = 1
    is_active: bool = True
    created_at: Optional[datetime] = None


class ResumeList(BaseModel):
    resumes: list[ResumeResponse]
    total: int
