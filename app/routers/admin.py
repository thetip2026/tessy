"""
FastAPI router: Admin panel — session-protected login + order management.
"""
import hmac
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.config import settings
from app.db.base import SessionLocal, get_db
from app.models.models import Order, OrderItem, PaymentEvent, User
from app.utils.crypto import constant_time_equal
from app.bot_instance import bot

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")


# ── Auth helpers ─────────────────────────────────────────────────────────────

def require_admin_session(request: Request):
    if request.session.get("is_admin") is not True:
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})


# ── Login ─────────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    username_ok = constant_time_equal(username, settings.admin_username)
    password_ok = constant_time_equal(password, settings.admin_password)
    if username_ok and password_ok:
        request.session["is_admin"] = True
        return RedirectResponse("/admin/ui", status_code=303)
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Invalid credentials."},
        status_code=401,
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


# ── Orders list ───────────────────────────────────────────────────────────────

@router.get("/ui", response_class=HTMLResponse)
async def admin_orders(request: Request, _: None = Depends(require_admin_session)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Order).order_by(Order.created_at.desc()).limit(200)
        )
        orders = q.scalars().all()
    return templates.TemplateResponse(
        "admin_orders.html",
        {"request": request, "orders": orders},
    )


# ── Order detail ──────────────────────────────────────────────────────────────

@router.get("/ui/orders/{order_public_id}", response_class=HTMLResponse)
async def admin_order_detail(
    order_public_id: str,
    request: Request,
    _: None = Depends(require_admin_session),
):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Order)
            .where(Order.public_id == order_public_id)
        )
        order = q.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        q_items = await session.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        items = q_items.scalars().all()
        q_events = await session.execute(
            select(PaymentEvent)
            .where(PaymentEvent.order_id == order.id)
            .order_by(PaymentEvent.created_at.desc())
        )
        events = q_events.scalars().all()
        q_user = await session.execute(
            select(User).where(User.id == order.user_id)
        )
        user = q_user.scalar_one_or_none()
    return templates.TemplateResponse(
        "admin_order_detail.html",
        {
            "request": request,
            "order": order,
            "items": items,
            "events": events,
            "user": user,
        },
    )


# ── Dispatch action ───────────────────────────────────────────────────────────

@router.post("/ui/orders/{order_public_id}/dispatch")
async def dispatch_order(
    order_public_id: str,
    request: Request,
    _: None = Depends(require_admin_session),
):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Order).where(Order.public_id == order_public_id)
        )
        order = q.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        q_user = await session.execute(select(User).where(User.id == order.user_id))
        user = q_user.scalar_one_or_none()

        order.status = "dispatched"
        await session.commit()

        if user:
            await bot.send_message(
                user.chat_id,
                "📦 Your order has been dispatched! Thank you for your purchase.",
            )
    return RedirectResponse(f"/admin/ui/orders/{order_public_id}", status_code=303)
