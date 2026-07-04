# ================================================================
# JARVIS CV
# ARQUIVO: auth.py
# DESCRIÇÃO: Rotas de autenticação - Registro, Login, Refresh, Reset
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
from fastapi import APIRouter, HTTPException, status, Depends
from jose import jwt
from datetime import datetime, timedelta

from app.config import settings
from app.models.user import UserRegister, UserLogin, UserResponse, TokenResponse, PasswordReset
from app.utils.supabase_client import supabase_client
from app.utils.logger import logger
from app.dependencies import get_current_user

router = APIRouter()


def _create_token(user_id: str, plan: str = "free") -> str:
    expires = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {"sub": user_id, "plan": plan, "exp": expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister):
    try:
        admin = supabase_client.admin_client
        auth_response = admin.auth.admin.create_user(
            {"email": body.email, "password": body.password, "email_confirm": True}
        )
        auth_user = auth_response.user
        profile = await supabase_client.create_profile(
            auth_id=auth_user.id, email=body.email, full_name=body.full_name
        )
        token = _create_token(profile["id"], "free")
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=profile["id"],
                email=body.email,
                full_name=body.full_name,
                plan="free",
                created_at=profile.get("created_at"),
            ),
        )
    except Exception as e:
        logger.error("[AUTH REGISTER ERROR]", str(e))
        raise HTTPException(status_code=400, detail=f"Erro ao criar conta: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    try:
        client = supabase_client.client
        auth_response = client.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
        auth_user = auth_response.user
        profile = await supabase_client.get_profile_by_auth_id(auth_user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado.")

        subscription = await supabase_client.get_subscription(profile["id"])
        plan = subscription.get("plan", "free") if subscription else "free"

        token = _create_token(profile["id"], plan)
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=profile["id"],
                email=body.email,
                full_name=profile.get("full_name"),
                plan=plan,
                created_at=profile.get("created_at"),
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[AUTH LOGIN ERROR]", str(e))
        raise HTTPException(status_code=401, detail="Email ou senha inválidos.")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(user: dict = Depends(get_current_user)):
    try:
        user_id = user["user_id"]
        profile = await supabase_client.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado.")

        subscription = await supabase_client.get_subscription(user_id)
        plan = subscription.get("plan", "free") if subscription else "free"

        token = _create_token(user_id, plan)
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user_id,
                email=profile.get("email", ""),
                full_name=profile.get("full_name", ""),
                plan=plan,
                created_at=profile.get("created_at"),
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[AUTH REFRESH ERROR]", str(e))
        raise HTTPException(status_code=401, detail="Não foi possível renovar o token.")


@router.post("/reset-password")
async def reset_password(body: PasswordReset):
    try:
        client = supabase_client.client
        client.auth.reset_password_for_email(body.email)
        return {"message": "Email de redefinição de senha enviado."}
    except Exception as e:
        logger.error("[AUTH RESET ERROR]", str(e))
        raise HTTPException(status_code=400, detail="Erro ao enviar email de redefinição.")
