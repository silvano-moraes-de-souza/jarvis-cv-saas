# ================================================================
# JARVIS CV
# ARQUIVO: dependencies.py
# DESCRIÇÃO: Dependências injetáveis - Auth, rate limiting, verificação de plano
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional

from app.config import settings
from app.utils.logger import logger

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """Decodifica JWT e retorna dados do usuário autenticado"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário.",
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return {"user_id": user_id, "plan": payload.get("plan", "free")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado ou inválido.")


async def require_plan(minimum_plan: str):
    """Factory que cria dependência para verificar plano mínimo do usuário"""
    plan_hierarchy = {"free": 0, "pro": 1, "elite": 2}

    async def _check_plan(user: dict = Depends(get_current_user)):
        user_plan = user.get("plan", "free")
        if plan_hierarchy.get(user_plan, 0) < plan_hierarchy.get(minimum_plan, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Esta funcionalidade requer o plano {minimum_plan.upper()}.",
            )
        return user

    return _check_plan


async def check_rate_limit(request: Request, user: dict = Depends(get_current_user)):
    """Verifica limites de uso diário baseado no plano do usuário"""
    plan = user.get("plan", "free")
    limits = settings.plan_limits.get(plan, settings.plan_limits["free"])
    return limits
