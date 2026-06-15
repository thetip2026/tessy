from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛍 Listings", callback_data="listings"),
            InlineKeyboardButton(text="ℹ️ About", callback_data="about"),
        ],
        [
            InlineKeyboardButton(text="❓ FAQ", callback_data="faq"),
            InlineKeyboardButton(text="⭐ Rating", callback_data="rating"),
        ],
        [
            InlineKeyboardButton(text="🔐 PGP", callback_data="pgp"),
            InlineKeyboardButton(text="📦 Orders", callback_data="my_orders"),
        ],
        [
            InlineKeyboardButton(text="💌 Contact", callback_data="contact"),
        ],
    ])


def category_keyboard(categories) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"cat:{cat.slug}")]
        for cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_keyboard(products) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=p.name, callback_data=f"prod:{p.id}")]
        for p in products
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="listings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_detail_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Add to Cart", callback_data=f"addcart:{product_id}"),
            InlineKeyboardButton(text="❤️ Wishlist", callback_data=f"wishlist:{product_id}"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="listings")],
    ])


def cart_keyboard(total: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🛒 Cart  £{total:.2f}", callback_data="view_cart")],
        [InlineKeyboardButton(text="⬅️ Main Menu", callback_data="main_menu")],
    ])


def checkout_keyboard(can_checkout: bool) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💳 Payment Method", callback_data="set_payment")],
        [InlineKeyboardButton(text="📬 Delivery Address", callback_data="set_address")],
        [InlineKeyboardButton(text="🚚 Delivery Method", callback_data="set_delivery")],
    ]
    if can_checkout:
        buttons.append(
            [InlineKeyboardButton(text="✅ Checkout", callback_data="checkout")]
        )
    buttons.append([InlineKeyboardButton(text="⬅️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_method_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="₿ Bitcoin (BTC)", callback_data="coin:btc")],
        [InlineKeyboardButton(text="🔵 Litecoin (LTC)", callback_data="coin:ltc")],
        [InlineKeyboardButton(text="🔒 Monero (XMR)", callback_data="coin:xmr")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="view_cart")],
    ])


def delivery_method_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📮 Standard Post", callback_data="delivery:standard")],
        [InlineKeyboardButton(text="⚡ Express Post", callback_data="delivery:express")],
        [InlineKeyboardButton(text="🏠 Collection", callback_data="delivery:collection")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="view_cart")],
    ])


def invoice_keyboard(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh Status", callback_data=f"check_payment:{order_id}")],
        [InlineKeyboardButton(text="⬅️ Main Menu", callback_data="main_menu")],
    ])
