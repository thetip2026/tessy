"""
Aiogram router: all bot commands, messages, and callback-query handlers.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.db.base import SessionLocal
from app.models.models import Category, Product, CartItem
from app.services.orders import (
    get_or_create_user,
    get_open_order,
    cart_total,
    build_order_from_cart,
    money,
    can_checkout,
)
from app.services.payments import NowPaymentsService
from app.keyboards.inline import (
    main_menu_keyboard,
    category_keyboard,
    product_keyboard,
    product_detail_keyboard,
    cart_keyboard,
    checkout_keyboard,
    payment_method_keyboard,
    delivery_method_keyboard,
    invoice_keyboard,
)
from app.templates import messages as msg
from app.states import CheckoutStates

router = Router()
payment_service = NowPaymentsService()


# ── /start ──────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message):
    async with SessionLocal() as session:
        await get_or_create_user(session, message.from_user)
    await message.answer(msg.WELCOME, parse_mode="Markdown", reply_markup=main_menu_keyboard())


# ── Main menu callbacks ──────────────────────────────────────────────────────

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(msg.WELCOME, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    await call.answer()


@router.callback_query(F.data == "about")
async def cb_about(call: CallbackQuery):
    await call.message.edit_text(msg.ABOUT, parse_mode="Markdown",
                                  reply_markup=main_menu_keyboard())
    await call.answer()


@router.callback_query(F.data == "faq")
async def cb_faq(call: CallbackQuery):
    await call.message.edit_text(msg.FAQ, parse_mode="Markdown",
                                  reply_markup=main_menu_keyboard())
    await call.answer()


@router.callback_query(F.data == "rating")
async def cb_rating(call: CallbackQuery):
    await call.message.edit_text(msg.RATING, parse_mode="Markdown",
                                  reply_markup=main_menu_keyboard())
    await call.answer()


@router.callback_query(F.data == "pgp")
async def cb_pgp(call: CallbackQuery):
    await call.message.edit_text(msg.PGP, parse_mode="Markdown",
                                  reply_markup=main_menu_keyboard())
    await call.answer()


@router.callback_query(F.data == "contact")
async def cb_contact(call: CallbackQuery):
    await call.message.edit_text(msg.CONTACT, parse_mode="Markdown",
                                  reply_markup=main_menu_keyboard())
    await call.answer()


# ── Listings ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "listings")
async def cb_listings(call: CallbackQuery):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Category).where(Category.parent_id.is_(None))
        )
        categories = q.scalars().all()
    await call.message.edit_text(
        msg.LISTINGS_INTRO,
        parse_mode="Markdown",
        reply_markup=category_keyboard(categories),
    )
    await call.answer()


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(call: CallbackQuery):
    slug = call.data.split(":", 1)[1]
    async with SessionLocal() as session:
        q_cat = await session.execute(select(Category).where(Category.slug == slug))
        category = q_cat.scalar_one_or_none()
        if not category:
            await call.answer("Category not found.", show_alert=True)
            return
        q_prod = await session.execute(
            select(Product)
            .where(Product.category_id == category.id)
            .where(Product.is_active.is_(True))
        )
        products = q_prod.scalars().all()
    if not products:
        await call.message.edit_text(msg.NO_PRODUCTS, reply_markup=main_menu_keyboard())
    else:
        await call.message.edit_text(
            f"🗂 *{category.name}*\n\nChoose a product:",
            parse_mode="Markdown",
            reply_markup=product_keyboard(products),
        )
    await call.answer()


@router.callback_query(F.data.startswith("prod:"))
async def cb_product(call: CallbackQuery):
    product_id = int(call.data.split(":", 1)[1])
    async with SessionLocal() as session:
        q = await session.execute(select(Product).where(Product.id == product_id))
        product = q.scalar_one_or_none()
    if not product:
        await call.answer("Product not found.", show_alert=True)
        return
    text = msg.PRODUCT_CARD.format(
        name=product.name,
        description=product.description,
        price=product.fiat_price,
        stock=product.stock_label or "In Stock",
        rating=product.rating,
        reviews=product.review_count,
    )
    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=product_detail_keyboard(product.id),
    )
    await call.answer()


# ── Cart ──────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("addcart:"))
async def cb_add_to_cart(call: CallbackQuery):
    product_id = int(call.data.split(":", 1)[1])
    async with SessionLocal() as session:
        user = await get_or_create_user(session, call.from_user)
        existing = await session.execute(
            select(CartItem)
            .where(CartItem.user_id == user.id)
            .where(CartItem.product_id == product_id)
        )
        item = existing.scalar_one_or_none()
        if item:
            item.quantity += 1
        else:
            session.add(CartItem(user_id=user.id, product_id=product_id, quantity=1))
        await session.commit()
        total = await cart_total(session, user)
    await call.answer(f"Added to cart. Total: {money(total)}", show_alert=False)
    await call.message.edit_reply_markup(reply_markup=cart_keyboard(total))


@router.callback_query(F.data == "view_cart")
async def cb_view_cart(call: CallbackQuery):
    async with SessionLocal() as session:
        user = await get_or_create_user(session, call.from_user)
        q = await session.execute(
            select(CartItem, Product)
            .join(Product, CartItem.product_id == Product.id)
            .where(CartItem.user_id == user.id)
        )
        rows = q.all()
        order = await get_open_order(session, user)
    if not rows:
        await call.message.edit_text(msg.CART_EMPTY, reply_markup=main_menu_keyboard())
        await call.answer()
        return
    lines = "\n".join(
        f"• {p.name} × {c.quantity} — {money(p.fiat_price * c.quantity)}"
        for c, p in rows
    )
    total = sum(p.fiat_price * c.quantity for c, p in rows)
    text = msg.CART_SUMMARY.format(items=lines, total=total)
    ready = order and can_checkout(order) if order else False
    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=checkout_keyboard(ready),
    )
    await call.answer()


# ── Checkout flow ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "set_payment")
async def cb_set_payment(call: CallbackQuery):
    await call.message.edit_text(
        "Choose your payment coin:",
        reply_markup=payment_method_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("coin:"))
async def cb_coin_chosen(call: CallbackQuery):
    coin = call.data.split(":", 1)[1]
    async with SessionLocal() as session:
        user = await get_or_create_user(session, call.from_user)
        order = await get_open_order(session, user)
        if not order:
            order = await build_order_from_cart(session, user)
        order.payment_method = coin
        order.coin = coin
        await session.commit()
        ready = can_checkout(order)
    await call.message.edit_text(
        f"✅ Payment method set to *{coin.upper()}*.",
        parse_mode="Markdown",
        reply_markup=checkout_keyboard(ready),
    )
    await call.answer()


@router.callback_query(F.data == "set_address")
async def cb_set_address(call: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutStates.waiting_address)
    await call.message.answer("📬 Please type your delivery address:")
    await call.answer()


@router.message(CheckoutStates.waiting_address)
async def process_address(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        user = await get_or_create_user(session, message.from_user)
        order = await get_open_order(session, user)
        if not order:
            order = await build_order_from_cart(session, user)
        order.delivery_address = message.text
        await session.commit()
        ready = can_checkout(order)
    await state.clear()
    await message.answer(
        "✅ Address saved.",
        reply_markup=checkout_keyboard(ready),
    )


@router.callback_query(F.data == "set_delivery")
async def cb_set_delivery(call: CallbackQuery):
    await call.message.edit_text(
        "🚚 Choose a delivery method:",
        reply_markup=delivery_method_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("delivery:"))
async def cb_delivery_chosen(call: CallbackQuery):
    method = call.data.split(":", 1)[1]
    async with SessionLocal() as session:
        user = await get_or_create_user(session, call.from_user)
        order = await get_open_order(session, user)
        if not order:
            order = await build_order_from_cart(session, user)
        order.delivery_method = method
        await session.commit()
        ready = can_checkout(order)
    await call.message.edit_text(
        f"✅ Delivery method set to *{method}*.",
        parse_mode="Markdown",
        reply_markup=checkout_keyboard(ready),
    )
    await call.answer()


@router.callback_query(F.data == "checkout")
async def cb_checkout(call: CallbackQuery):
    async with SessionLocal() as session:
        user = await get_or_create_user(session, call.from_user)
        order = await get_open_order(session, user)
        if not order or not can_checkout(order):
            await call.answer("Please complete all checkout fields first.", show_alert=True)
            return
        # Create payment with NOWPayments
        try:
            resp = await payment_service.create_payment(
                order_id=order.public_id,
                price_amount=order.fiat_total,
                pay_currency=order.coin,
                order_description=f"Order {order.public_id}",
            )
        except Exception as e:
            await call.answer(f"Payment creation failed: {e}", show_alert=True)
            return
        order.payment_address = resp.get("pay_address")
        order.coin_amount = resp.get("pay_amount")
        order.provider_payment_id = str(resp.get("payment_id", ""))
        order.provider_payment_status = resp.get("payment_status", "waiting")
        order.status = "awaiting_payment"
        order.expires_at = payment_service.expiry()
        await session.commit()
        invoice_text = msg.ORDER_INVOICE.format(
            order_id=order.public_id,
            coin_amount=order.coin_amount,
            coin=order.coin.upper(),
            address=order.payment_address,
        )
    await call.message.edit_text(
        invoice_text,
        parse_mode="Markdown",
        reply_markup=invoice_keyboard(order.public_id),
    )
    await call.answer()


@router.callback_query(F.data == "my_orders")
async def cb_my_orders(call: CallbackQuery):
    async with SessionLocal() as session:
        user = await get_or_create_user(session, call.from_user)
        order = await get_open_order(session, user)
    if not order:
        await call.message.edit_text(msg.NO_OPEN_ORDER, reply_markup=main_menu_keyboard())
    else:
        await call.message.edit_text(
            f"📦 *Order #{order.public_id}*\nStatus: `{order.status}`",
            parse_mode="Markdown",
            reply_markup=invoice_keyboard(order.public_id) if order.payment_address else main_menu_keyboard(),
        )
    await call.answer()
