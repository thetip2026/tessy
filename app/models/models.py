from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    chat_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    fiat_price: Mapped[float] = mapped_column(Float)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=5.0)
    stock_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    flavour_options: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    public_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(64), default="pending_checkout")
    fiat_currency: Mapped[str] = mapped_column(String(12), default="gbp")
    fiat_total: Mapped[float] = mapped_column(Float, default=0)
    coin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    coin_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    payment_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_payment_id: Mapped[str | None] = mapped_column(
        String(120), nullable=True, index=True
    )
    provider_payment_status: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    discount_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shipping_cost: Mapped[float] = mapped_column(Float, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    title: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[float] = mapped_column(Float)
    unit_price: Mapped[float] = mapped_column(Float)


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    provider: Mapped[str] = mapped_column(String(50), default="nowpayments")
    provider_payment_id: Mapped[str | None] = mapped_column(
        String(120), nullable=True, index=True
    )
    external_status: Mapped[str] = mapped_column(String(120))
    raw_payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
