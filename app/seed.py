"""
Seed the database with demo categories and products on first start.
Edit or remove this file once you have real listings.
"""
from sqlalchemy import select
from app.db.base import SessionLocal
from app.models.models import Category, Product


async def seed_data():
    async with SessionLocal() as session:
        # Only seed if no categories exist
        existing = await session.execute(select(Category).limit(1))
        if existing.scalar_one_or_none():
            return

        ebooks = Category(name="E-Books", slug="ebooks")
        physicals = Category(name="Physical Items", slug="physical")
        digital = Category(name="Digital Services", slug="digital")
        session.add_all([ebooks, physicals, digital])
        await session.flush()

        session.add_all([
            Product(
                category_id=ebooks.id,
                name="Privacy Guide 2024",
                slug="privacy-guide-2024",
                description="A comprehensive guide to digital privacy and OpSec.",
                fiat_price=9.99,
                stock_label="In Stock",
                rating=4.9,
                review_count=47,
            ),
            Product(
                category_id=physicals.id,
                name="Sticker Pack Vol.1",
                slug="sticker-pack-v1",
                description="High-quality vinyl stickers, anonymous delivery.",
                fiat_price=4.99,
                stock_label="In Stock",
                rating=5.0,
                review_count=12,
            ),
            Product(
                category_id=digital.id,
                name="VPN Setup Service",
                slug="vpn-setup",
                description="Custom VPN configuration with hardened settings.",
                fiat_price=19.99,
                stock_label="Available",
                rating=4.8,
                review_count=30,
            ),
        ])
        await session.commit()
