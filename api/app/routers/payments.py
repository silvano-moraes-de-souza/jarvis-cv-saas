# ================================================================
# JARVIS CV
# ARQUIVO: payments.py
# DESCRIÇÃO: Rotas de pagamentos - Stripe checkout, webhooks, gestão de assinatura
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
import stripe
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from typing import Optional

from app.config import settings
from app.dependencies import get_current_user
from app.utils.supabase_client import supabase_client
from app.utils.logger import logger

router = APIRouter()
stripe.api_key = settings.stripe_secret_key

PLAN_PRICE_MAP = {
    "pro": settings.stripe_pro_price_id,
    "elite": settings.stripe_elite_price_id,
}


@router.post("/checkout")
async def create_checkout_session(
    plan: str,
    user: dict = Depends(get_current_user),
):
    if plan not in PLAN_PRICE_MAP:
        raise HTTPException(status_code=400, detail="Plano inválido. Use: pro ou elite.")

    price_id = PLAN_PRICE_MAP[plan]
    if not price_id:
        raise HTTPException(status_code=503, detail="Pagamentos não configurados.")

    try:
        profile = await supabase_client.get_profile(user["user_id"])
        customer_email = profile.get("email", "") if profile else ""

        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            customer_email=customer_email or None,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url="http://localhost:5173/dashboard?checkout=success",
            cancel_url="http://localhost:5173/pricing?checkout=cancelled",
            metadata={"user_id": user["user_id"], "plan": plan},
        )
        return {"url": session.url, "session_id": session.id}
    except Exception as e:
        logger.error("[STRIPE CHECKOUT ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao criar sessão de pagamento.")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    body = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            body, sig_header, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Assinatura webhook inválida.")
    except Exception:
        raise HTTPException(status_code=400, detail="Payload webhook inválido.")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data["metadata"].get("user_id")
        plan = data["metadata"].get("plan", "free")
        if user_id:
            await supabase_client.update_subscription(user_id, plan, "active")
            logger.log(f"Assinatura {plan} ativada para usuário {user_id}")

    elif event_type == "customer.subscription.updated":
        customer_id = data["customer"]
        new_status = data["status"]
        plan = data.get("plan", {}).get("nickname", "free")
        logger.log(f"Assinatura {customer_id} atualizada: {new_status}")

    elif event_type == "customer.subscription.deleted":
        customer_id = data["customer"]
        logger.log(f"Assinatura {customer_id} cancelada")

    return {"received": True}


@router.get("/subscription")
async def get_subscription(user: dict = Depends(get_current_user)):
    subscription = await supabase_client.get_subscription(user["user_id"])
    if not subscription:
        return {"plan": "free", "status": "active"}
    return subscription


@router.post("/cancel")
async def cancel_subscription(user: dict = Depends(get_current_user)):
    subscription = await supabase_client.get_subscription(user["user_id"])
    if not subscription or subscription.get("plan") == "free":
        raise HTTPException(status_code=400, detail="Nenhuma assinatura ativa para cancelar.")

    try:
        stripe_sub_id = subscription.get("stripe_subscription_id")
        if stripe_sub_id:
            stripe.Subscription.delete(stripe_sub_id)
        await supabase_client.update_subscription(user["user_id"], "free", "cancelled")
        return {"message": "Assinatura cancelada com sucesso."}
    except Exception as e:
        logger.error("[STRIPE CANCEL ERROR]", str(e))
        raise HTTPException(status_code=500, detail="Erro ao cancelar assinatura.")
