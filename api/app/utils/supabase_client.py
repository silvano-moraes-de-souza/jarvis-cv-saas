# ================================================================
# JARVIS CV
# ARQUIVO: supabase_client.py
# DESCRIÇÃO: Cliente Supabase singleton para operações de banco de dados
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
from supabase import create_client, Client
from typing import Optional

from app.config import settings
from app.utils.logger import logger


class SupabaseClient:
    """Cliente Supabase singleton com métodos utilitários"""

    _instance: Optional["SupabaseClient"] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = create_client(
                settings.supabase_url, settings.supabase_service_key or settings.supabase_key
            )
            logger.log("Cliente Supabase inicializado")
        return self._client

    @property
    def admin_client(self) -> Client:
        return create_client(settings.supabase_url, settings.supabase_service_key)

    async def get_profile(self, user_id: str) -> Optional[dict]:
        response = self.client.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None

    async def get_profile_by_auth_id(self, auth_id: str) -> Optional[dict]:
        response = self.client.table("profiles").select("*").eq("auth_id", auth_id).execute()
        return response.data[0] if response.data else None

    async def create_profile(self, auth_id: str, email: str, full_name: str = None) -> dict:
        data = {"auth_id": auth_id, "email": email}
        if full_name:
            data["full_name"] = full_name
        response = self.client.table("profiles").insert(data).execute()
        return response.data[0] if response.data else {}

    async def update_subscription(self, user_id: str, plan: str, status: str = "active") -> dict:
        response = (
            self.client.table("subscriptions")
            .upsert({"user_id": user_id, "plan": plan, "status": status})
            .execute()
        )
        return response.data[0] if response.data else {}

    async def get_subscription(self, user_id: str) -> Optional[dict]:
        response = self.client.table("subscriptions").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    async def log_usage(self, user_id: str, action: str) -> dict:
        response = (
            self.client.table("usage_logs")
            .insert({"user_id": user_id, "action": action})
            .execute()
        )
        return response.data[0] if response.data else {}

    async def get_daily_usage(self, user_id: str, action: str) -> int:
        response = (
            self.client.table("usage_logs")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("action", action)
            .gte("created_at", "today")
            .execute()
        )
        return response.count if response.count else 0


supabase_client = SupabaseClient()
