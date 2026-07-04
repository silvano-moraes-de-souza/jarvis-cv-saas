# ================================================================
# JARVIS CV
# ARQUIVO: run.py
# DESCRIÇÃO: Script de inicialização do servidor FastAPI via Uvicorn
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.api_env == "development",
        log_level="info",
    )
