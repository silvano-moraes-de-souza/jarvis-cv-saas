# ================================================================
# JARVIS CV
# ARQUIVO: health.py
# DESCRIÇÃO: Rotas de saúde do sistema - Status, versão, verificações
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": "JARVIS CV API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/version")
async def version():
    return {"version": "2.0.0", "api": "JARVIS CV", "engine": "NVIDIA Qwen 3.5 122B"}
