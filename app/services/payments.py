from datetime import datetime, timedelta
import httpx
from app.config import settings


class NowPaymentsService:
    def __init__(self):
        self.base_url = settings.nowpayments_base_url
        self.headers = {
            "x-api-key": settings.nowpayments_api_key,
            "Content-Type": "application/json",
        }

    async def create_payment(
        self,
        order_id: str,
        price_amount: float,
        pay_currency: str,
        order_description: str,
    ) -> dict:
        """
        Create a NOWPayments payment and return the full response dict.
        Response includes: pay_address, pay_amount, payment_id, payment_status, etc.
        Supported pay_currency values: btc, ltc, xmr (and many others).
        """
        payload = {
            "price_amount": price_amount,
            "price_currency": settings.default_currency,
            "pay_currency": pay_currency.lower(),
            "order_id": order_id,
            "order_description": order_description,
            "ipn_callback_url": f"{settings.base_url}/webhooks/nowpayments",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{self.base_url}/payment",
                headers=self.headers,
                json=payload,
            )
            r.raise_for_status()
            return r.json()

    async def get_payment_status(self, payment_id: str) -> dict:
        """Poll current status for a specific payment ID."""
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                f"{self.base_url}/payment/{payment_id}",
                headers=self.headers,
            )
            r.raise_for_status()
            return r.json()

    def expiry(self) -> datetime:
        return datetime.utcnow() + timedelta(minutes=settings.order_expiry_minutes)
