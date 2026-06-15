"""
FastAPI router: NOWPayments IPN webhook endpoint.
"""
import json
from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import select

from app.config import settings
from app.db.base import SessionLocal
from app.models.models import Order, PaymentEvent, User
from app.utils.crypto import verify_nowpayments_signature
from app.bot_instance import bot

router = APIRouter()


@router.post("/webhooks/nowpayments")
async def nowpayments_webhook(
    request: Request,
    x_nowpayments_sig: str | None = Header(default=None),
):
    raw = await request.body()

    # 1. Signature verification
    if not x_nowpayments_sig or not verify_nowpayments_signature(
        raw, x_nowpayments_sig, settings.nowpayments_ipn_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(raw.decode("utf-8"))
    order_id = payload.get("order_id")
    provider_payment_id = str(payload.get("payment_id") or "")
    payment_status = payload.get("payment_status", "unknown")
    pay_currency = str(payload.get("pay_currency") or "").upper()
    pay_amount = payload.get("pay_amount")

    async with SessionLocal() as session:
        q = await session.execute(
            select(Order, User)
            .join(User, Order.user_id == User.id)
            .where(Order.public_id == order_id)
        )
        row = q.first()
        if not row:
            # Unknown order — return 200 so NOWPayments stops retrying
            return {"ok": True}
        order, user = row

        # 2. Consistency checks
        if (
            order.provider_payment_id
            and provider_payment_id
            and order.provider_payment_id != provider_payment_id
        ):
            raise HTTPException(status_code=400, detail="Payment ID mismatch")
        if order.coin and pay_currency and order.coin.upper() != pay_currency:
            raise HTTPException(status_code=400, detail="Currency mismatch")
        if (
            order.coin_amount
            and pay_amount is not None
            and abs(float(order.coin_amount) - float(pay_amount)) > 1e-8
        ):
            raise HTTPException(status_code=400, detail="Amount mismatch")

        # 3. Idempotency check
        existing = await session.execute(
            select(PaymentEvent).where(
                PaymentEvent.order_id == order.id,
                PaymentEvent.provider_payment_id == provider_payment_id,
                PaymentEvent.external_status == payment_status,
            )
        )
        if existing.scalar_one_or_none():
            return {"ok": True, "duplicate": True}

        # 4. Record the event
        session.add(
            PaymentEvent(
                order_id=order.id,
                provider_payment_id=provider_payment_id or None,
                external_status=payment_status,
                raw_payload=json.dumps(payload),
            )
        )
        order.provider_payment_status = payment_status

        # 5. Update order status and notify buyer via Telegram chat_id
        terminal_statuses = {"paid_awaiting_dispatch", "dispatched"}
        if payment_status in {"confirming", "partially_paid"} and order.status not in terminal_statuses:
            order.status = "payment_detected"
            await bot.send_message(user.chat_id, "✅ Payment detected — waiting for blockchain confirmations.")
        elif payment_status in {"confirmed", "finished"} and order.status not in terminal_statuses:
            order.status = "paid_awaiting_dispatch"
            await bot.send_message(user.chat_id, "🎉 Payment confirmed! Your order is awaiting dispatch.")
        elif payment_status in {"expired", "failed"} and order.status not in terminal_statuses:
            order.status = "expired"
            await bot.send_message(user.chat_id, "⏱ Payment expired or failed. Please place a new order.")

        await session.commit()
    return {"ok": True}
