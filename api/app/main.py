# ================================================================
# JARVIS CV
# ARQUIVO: main.py
# DESCRIÇÃO: Entry point da aplicação FastAPI - Rotas, middleware, CORS
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.routers import auth, resumes, analysis, jobs, documents, payments, health, linkedin

app = FastAPI(
    title="JARVIS CV API",
    description="Plataforma SaaS de Otimização de Carreira com IA",
    version="3.0.0",
    docs_url="/api/docs" if settings.api_env == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["Currículos"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Análise ATS"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Vagas"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documentos"])
app.include_router(linkedin.router, prefix="/api/linkedin", tags=["LinkedIn"])
app.include_router(payments.router, prefix="/api/payments", tags=["Pagamentos"])
app.include_router(health.router, prefix="/api", tags=["Sistema"])


@app.on_event("startup")
async def startup():
    """Inicialização: conexão Redis, verificação de serviços"""
    pass


@app.on_event("shutdown")
async def shutdown():
    """Encerramento: fechamento de conexões"""
    pass
