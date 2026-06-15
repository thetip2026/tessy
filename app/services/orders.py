from uuid import uuid4
from sqlalchemy import select, delete
from app.models.models import User, Product, CartItem, Order, OrderItem, Category
from app.services.payments import NowPaymentsService

payment_service = NowPaymentsService()


def money(value: float) -> str:
    return f"£{value:.2f}"


def can_checkout(order: Order) -> bool:
    return bool(
        order.payment_method and order.delivery_address and order.delivery_method
    )


async def get_or_create_user(session, telegram_user):
    """Upsert a Telegram user record, keeping chat_id in sync."""
    q = await session.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = q.scalar_one_or_none()
    if user:
        user.chat_id = telegram_user.id
        user.username = telegram_user.username
        user.full_name = telegram_user.full_name
        await session.commit()
        return user
    user = User(
        telegram_id=telegram_user.id,
        chat_id=telegram_user.id,
        username=telegram_user.username,
        full_name=telegram_user.full_name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_open_order(session, user: User) -> Order | None:
    """Return the user's most recent non-terminal order, or None."""
    terminal = {"dispatched", "expired", "cancelled"}
    q = await session.execute(
        select(Order)
        .where(Order.user_id == user.id)
        .where(Order.status.notin_(terminal))
        .order_by(Order.id.desc())
    )
    return q.scalar_one_or_none()


async def cart_total(session, user: User) -> float:
    """Sum the fiat total of all items currently in the user's cart."""
    q = await session.execute(
        select(CartItem, Product)
        .join(Product, CartItem.product_id == Product.id)
        .where(CartItem.user_id == user.id)
    )
    rows = q.all()
    return sum(p.fiat_price * c.quantity for c, p in rows)


async def build_order_from_cart(session, user: User) -> Order:
    """Convert the user's cart into a new Order with OrderItems."""
    q = await session.execute(
        select(CartItem, Product)
        .join(Product, CartItem.product_id == Product.id)
        .where(CartItem.user_id == user.id)
    )
    rows = q.all()
    total = sum(p.fiat_price * c.quantity for c, p in rows)
    order = Order(
        user_id=user.id,
        public_id=uuid4().hex[:16],
        fiat_total=total,
        status="pending_checkout",
    )
    session.add(order)
    await session.flush()  # get order.id before adding items
    for cart_item, product in rows:
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                title=product.name,
                quantity=cart_item.quantity,
                unit_price=product.fiat_price,
            )
        )
    # Clear the cart
    await session.execute(
        delete(CartItem).where(CartItem.user_id == user.id)
    )
    await session.commit()
    await session.refresh(order)
    return order
