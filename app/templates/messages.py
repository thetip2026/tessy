"""Telegram message text templates. Edit these to customise your bot's copy."""

WELCOME = (
    "👋 *Welcome to the shop!*\n\n"
    "Browse listings, add items to your cart, and pay securely with crypto.\n\n"
    "Use the buttons below to navigate."
)

ABOUT = (
    "ℹ️ *About*\n\n"
    "We are an anonymous service accepting BTC, LTC, and XMR.\n"
    "All orders are handled discretely."
)

FAQ = (
    "❓ *FAQ*\n\n"
    "• *How long does dispatch take?* — 1–3 business days after payment is confirmed.\n"
    "• *Do you offer refunds?* — Contact us within 24 hours of receiving your order.\n"
    "• *Is XMR accepted?* — Yes, all three coins are accepted.\n"
    "• *How do I track my order?* — Use the 📦 Orders button."
)

RATING = (
    "⭐ *Rating*\n\n"
    "We maintain a 5-star rating based on verified buyer feedback.\n"
    "Ratings are updated weekly."
)

PGP = (
    "🔐 *PGP Key*\n\n"
    "```\n"
    "-----BEGIN PGP PUBLIC KEY BLOCK-----\n"
    "[PASTE YOUR PGP PUBLIC KEY HERE]\n"
    "-----END PGP PUBLIC KEY BLOCK-----\n"
    "```"
)

CONTACT = (
    "💌 *Contact*\n\n"
    "Open a support ticket by messaging @YourSupportUsername\n"
    "or reply to this bot with your question."
)

LISTINGS_INTRO = "🛍 *Choose a category:*"

NO_PRODUCTS = "⚠️ No products available in this category right now."

PRODUCT_CARD = (
    "🏷 *{name}*\n\n"
    "{description}\n\n"
    "💰 Price: £{price:.2f}\n"
    "📦 Stock: {stock}\n"
    "⭐ Rating: {rating}/5 ({reviews} reviews)"
)

CART_EMPTY = "🛒 Your cart is empty. Browse Listings to add items."

CART_SUMMARY = (
    "🛒 *Your Cart*\n\n"
    "{items}\n"
    "─────────────\n"
    "💰 *Total: £{total:.2f}*\n\n"
    "Set your delivery address, delivery method, and payment coin to unlock Checkout."
)

ORDER_INVOICE = (
    "🧾 *Order #{order_id}*\n\n"
    "💰 Amount: `{coin_amount} {coin}`\n"
    "📬 Address:\n`{address}`\n\n"
    "⏳ Send the exact amount to the address above.\n"
    "Status updates will appear here automatically."
)

PAYMENT_DETECTED = "✅ Payment detected — waiting for blockchain confirmations."
PAYMENT_CONFIRMED = "🎉 Payment confirmed! Your order is awaiting dispatch."
PAYMENT_EXPIRED = "⏱ Payment window expired. Please place a new order."
ORDER_DISPATCHED = "📦 Your order has been dispatched! Thank you for your purchase."

NO_OPEN_ORDER = "You don't have an active order. Start by adding items to your cart."
