# ================================================================
# JARVIS CV
# ARQUIVO: celery_worker.py
# DESCRIÇÃO: Worker Celery para processamento assíncrono de análises de IA
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
from celery import Celery

from app.config import settings
from app.utils.logger import logger

celery_app = Celery(
    "jarvis_cv",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_max_tasks_per_child=50,
)


@celery_app.task(bind=True, name="process_ats_analysis")
def process_ats_analysis(self, cv_text: str, job_text: str, user_id: str, resume_id: str, job_id: str):
    import asyncio
    from app.services.ai_engine import ai_engine
    from app.utils.supabase_client import supabase_client
    import uuid

    try:
        self.update_state(state="PROCESSING", meta={"progress": 10})

        result = asyncio.run(ai_engine.analyze_ats(cv_text, job_text))
        self.update_state(state="PROCESSING", meta={"progress": 70})

        analysis_id = str(uuid.uuid4())
        data = {
            "id": analysis_id,
            "user_id": user_id,
            "resume_id": resume_id,
            "job_id": job_id,
            "score": result.get("score"),
            "gap_analysis": {
                "strengths": result.get("strengths", []),
                "weaknesses": result.get("weaknesses", []),
                "missing_skills": result.get("missing_skills", []),
            },
            "suggestions": {
                "rewritten_summary": result.get("rewritten_summary"),
                "suggested_headline": result.get("suggested_headline"),
                "recommendations": result.get("recommendations", []),
            },
        }
        supabase_client.client.table("optimization_results").insert(data).execute()
        asyncio.run(supabase_client.log_usage(user_id, "analysis"))

        self.update_state(state="COMPLETED", meta={"progress": 100})
        return {"analysis_id": analysis_id, "score": result.get("score")}
    except Exception as e:
        logger.error("[CELERY ATS ERROR]", str(e))
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery_app.task(bind=True, name="process_cover_letter")
def process_cover_letter(self, cv_text: str, job_text: str, tone: str, analysis_id: str, user_id: str):
    import asyncio
    from app.services.ai_engine import ai_engine
    from app.utils.supabase_client import supabase_client

    try:
        cover_letter = asyncio.run(ai_engine.generate_cover_letter(cv_text, job_text, tone))
        supabase_client.client.table("optimization_results").update(
            {"suggestions": {"cover_letter": cover_letter}}
        ).eq("id", analysis_id).execute()
        return {"analysis_id": analysis_id, "cover_letter_length": len(cover_letter)}
    except Exception as e:
        logger.error("[CELERY COVER LETTER ERROR]", str(e))
        raise
