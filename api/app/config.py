# ================================================================
# JARVIS CV
# ARQUIVO: config.py
# DESCRIÇÃO: Configurações centralizadas - Multi-model NVIDIA API
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 3.0.0
# ================================================================
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API
    api_port: int = 3001
    api_env: str = "development"

    # NVIDIA API - Multi-Model Architecture
    nvidia_api_key: str = ""
    nvidia_api_url: str = "https://integrate.api.nvidia.com/v1/chat/completions"

    # Modelos por propósito (otimizados para velocidade < 40s)
    nvidia_model_brain: str = "meta/llama-3.1-8b-instruct"
    nvidia_model_writer: str = "qwen/qwen2.5-coder-32b-instruct"
    nvidia_model_analyzer: str = "google/gemma-3-27b-it"
    nvidia_model_planner: str = "mistralai/mistral-7b-instruct-v0.3"
    nvidia_model_fast: str = "nvidia/nemotron-mini-4b-instruct"

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""
    stripe_elite_price_id: str = ""

    # JWT
    jwt_secret: str = "jarvis-cv-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Limites por plano
    plan_limits: dict = {
        "free": {"daily_analyses": 3, "daily_jobs": 3},
        "pro": {"daily_analyses": 15, "daily_jobs": 15},
        "elite": {"daily_analyses": 999, "daily_jobs": 999},
    }

    # Scoring ATS - Pesos do Motor Realista
    ats_weights: dict = {
        "keyword_match": 0.30,
        "skill_density": 0.20,
        "structure_quality": 0.15,
        "seniority_alignment": 0.15,
        "experience_relevance": 0.10,
        "format_ats_compatibility": 0.10,
    }

    # Portais de Vagas
    job_portals: dict = {
        "linkedin": {"base_url": "https://www.linkedin.com/jobs/search", "enabled": True},
        "indeed": {"base_url": "https://br.indeed.com/jobs", "enabled": True},
        "catho": {"base_url": "https://www.catho.com.br/vagas", "enabled": True},
        "gupy": {"base_url": "https://portal.gupy.io", "enabled": True},
        "remotar": {"base_url": "https://remotar.com.br", "enabled": True},
        "geekhunter": {"base_url": "https://www.geekhunter.com.br/vagas", "enabled": True},
        "programathor": {"base_url": "https://programathor.com.br/jobs", "enabled": True},
        "nerdin": {"base_url": "https://nerdin.com.br/vagas", "enabled": True},
        "infojobs": {"base_url": "https://www.infojobs.com.br", "enabled": True},
    }

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
