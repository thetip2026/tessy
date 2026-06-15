from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.config import settings
from app.security import admin_api_guard, constant_time_equal, require_admin_session
from app.db.base import SessionLocal
from app.models.models import Order, PaymentEvent, User
from app.bot_instance import bot

router = APIRouter(prefix='/admin')
templates = Jinja2Templates(directory='app/templates')

@router.get('/login', response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse('admin_login.html', {'request': request, 'title': 'Admin Login', 'error': None})

@router.post('/login', response_class=HTMLResponse)
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if constant_time_equal(username, settings.admin_username) and constant_time_equal(password, settings.admin_password):
        request.session['is_admin'] = True
        return RedirectResponse(url='/admin/ui', status_code=303)
    return templates.TemplateResponse('admin_login.html', {'request': request, 'title': 'Admin Login', 'error': 'Invalid credentials'}, status_code=401)

@router.post('/logout')
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/admin/login', status_code=303)

@router.get('/orders', dependencies=[Depends(admin_api_guard)])
async def list_orders_api():
    async with SessionLocal() as session:
        q = await session.execute(select(Order).order_by(Order.created_at.desc()))
        orders = q.scalars().all()
        return [
            {
                'id': o.public_id,
                'status': o.status,
                'total': o.fiat_total + (o.shipping_cost or 0),
                'coin': o.coin,
                'payment_status': o.provider_payment_status,
            }
            for o in orders
        ]

@router.post('/orders/{public_id}/dispatch', dependencies=[Depends(admin_api_guard)])
async def dispatch_order_api(public_id: str):
    async with SessionLocal() as session:
        q = await session.execute(select(Order, User).join(User, Order.user_id == User.id).where(Order.public_id == public_id))
        row = q.first()
        if not row:
            raise HTTPException(status_code=404, detail='Order not found')
        order, user = row
        order.status = 'dispatched'
        await session.commit()
        await bot.send_message(user.chat_id, '📦 Item dispatched')
        return {'ok': True, 'status': order.status}

@router.get('/ui', response_class=HTMLResponse)
async def admin_orders_page(request: Request):
    require_admin_session(request)
    async with SessionLocal() as session:
        q = await session.execute(select(Order).order_by(Order.created_at.desc()))
        orders = q.scalars().all()
        response = templates.TemplateResponse('admin_orders.html', {'request': request, 'orders': orders, 'title': 'Orders'})
        response.headers['Cache-Control'] = 'no-store'
        return response

@router.get('/ui/orders/{public_id}', response_class=HTMLResponse)
async def admin_order_detail_page(public_id: str, request: Request):
    require_admin_session(request)
    async with SessionLocal() as session:
        q = await session.execute(select(Order).where(Order.public_id == public_id))
        order = q.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail='Order not found')
        eq = await session.execute(select(PaymentEvent).where(PaymentEvent.order_id == order.id).order_by(PaymentEvent.created_at.desc()))
        events = eq.scalars().all()
        response = templates.TemplateResponse('admin_order_detail.html', {'request': request, 'order': order, 'events': events, 'title': f'Order {public_id}'})
        response.headers['Cache-Control'] = 'no-store'
        return response

@router.post('/ui/orders/{public_id}/dispatch')
async def admin_order_dispatch_action(public_id: str, request: Request):
    require_admin_session(request)
    async with SessionLocal() as session:
        q = await session.execute(select(Order, User).join(User, Order.user_id == User.id).where(Order.public_id == public_id))
        row = q.first()
        if not row:
            raise HTTPException(status_code=404, detail='Order not found')
        order, user = row
        order.status = 'dispatched'
        await session.commit()
        await bot.send_message(user.chat_id, '📦 Item dispatched')
    return RedirectResponse(url=f'/admin/ui/orders/{public_id}', status_code=303)
