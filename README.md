# Telegram Crypto Service Bot

A fully-featured Telegram storefront bot with:
- Category → product → cart → checkout flow
- BTC, LTC, and XMR (Monero) payments via [NOWPayments](https://nowpayments.io)
- In-message payment address display (no external links required)
- Automatic buyer notifications on payment detected / confirmed / dispatched
- Session-protected admin panel with order management and dispatch button
- Security headers, HMAC webhook verification, and idempotent event handling

---

## Project Layout

```
telegram-crypto-bot/
├── app/
│   ├── config.py              ← Pydantic settings (reads from .env)
│   ├── main.py                ← FastAPI app (API + admin panel)
│   ├── bot_instance.py        ← Aiogram bot + dispatcher
│   ├── states.py              ← FSM state groups
│   ├── seed.py                ← Demo data seeder (edit with real listings)
│   ├── db/
│   │   └── base.py            ← SQLAlchemy async engine + SessionLocal
│   ├── models/
│   │   └── models.py          ← ORM models (User, Category, Product, Order…)
│   ├── services/
│   │   ├── orders.py          ← Cart, order, and user helpers
│   │   └── payments.py        ← NOWPayments API client
│   ├── routers/
│   │   ├── bot.py             ← All Telegram handlers (commands + callbacks)
│   │   ├── webhooks.py        ← NOWPayments IPN endpoint
│   │   └── admin.py           ← Admin panel routes
│   ├── keyboards/
│   │   └── inline.py          ← All InlineKeyboardMarkup builders
│   ├── templates/
│   │   ├── messages.py        ← Bot message text (edit your copy here)
│   │   ├── admin_base.html
│   │   ├── admin_login.html
│   │   ├── admin_orders.html
│   │   └── admin_order_detail.html
│   ├── static/
│   │   └── admin.css          ← Admin panel dark-theme stylesheet
│   ├── utils/
│   │   └── crypto.py          ← HMAC helpers
│   └── middleware/
│       └── security_headers.py ← Security response headers
├── run_bot.py                 ← Bot process entry point
├── requirements.txt
├── .env.example               ← Copy to .env and fill in secrets
├── .gitignore
├── Procfile                   ← Railway/Render start commands
├── README.md                  ← This file
└── SETUP_GUIDE.md             ← Step-by-step deployment guide
```

---

## Quick Start (Local)

```bash
# 1. Clone / extract the project
cd telegram-crypto-bot

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and fill in environment variables
cp .env.example .env
# Edit .env — see "Environment Variables" section below

# 5. Terminal 1 — start the FastAPI server
uvicorn app.main:app --reload

# 6. Terminal 2 — start the Telegram bot
python run_bot.py
```

Open `http://127.0.0.1:8000/health` — you should see `{"ok": true}`.
Open `http://127.0.0.1:8000/admin/login` and sign in with your admin credentials.
Send `/start` to your bot in Telegram.

> **SECURE_COOKIES note:** Set `SECURE_COOKIES=false` for local HTTP testing.
> Always set it back to `true` in production (HTTPS).

---

## Environment Variables

All secrets live in `.env` (never commit this file — it is already in `.gitignore`).

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | Telegram bot token from @BotFather |
| `BOT_USERNAME` | ✅ | Bot username without @ (e.g. `myshop_bot`) |
| `BASE_URL` | ✅ | Public HTTPS URL of your FastAPI server |
| `WEBHOOK_SECRET` | ✅ | Long random secret for webhook integrity |
| `ADMIN_CHAT_IDS` | ✅ | Your Telegram numeric ID (comma-separated for multiple admins) |
| `ADMIN_API_KEY` | ✅ | Internal API key — generate with `openssl rand -hex 32` |
| `ADMIN_USERNAME` | ✅ | Admin panel login username |
| `ADMIN_PASSWORD` | ✅ | Admin panel login password |
| `SESSION_SECRET` | ✅ | Flask/Starlette session signing key — `openssl rand -hex 32` |
| `DATABASE_URL` | ✅ | SQLAlchemy URL. Default: `sqlite+aiosqlite:///./bot.db` |
| `NOWPAYMENTS_API_KEY` | ✅ | From your NOWPayments dashboard |
| `NOWPAYMENTS_IPN_SECRET` | ✅ | IPN secret from NOWPayments IPN settings |
| `NOWPAYMENTS_BASE_URL` | — | Defaults to `https://api.nowpayments.io/v1` |
| `DEFAULT_CURRENCY` | — | Fiat currency for pricing (default: `gbp`) |
| `ORDER_EXPIRY_MINUTES` | — | Payment window duration (default: `90`) |
| `REDIS_URL` | — | Redis connection URL (needed for production FSM) |
| `SECURE_COOKIES` | — | `true` in production, `false` for local HTTP |

### Generating secrets quickly

```bash
openssl rand -hex 32   # use for SESSION_SECRET, ADMIN_API_KEY, WEBHOOK_SECRET
```

### Managing env vars on Railway

1. Open your Railway project → select a service → **Variables** tab.
2. Add each variable from the table above.
3. Set `BASE_URL` to the Railway-generated public domain, e.g. `https://your-app.up.railway.app`.
4. Set `SECURE_COOKIES=true`.

### Managing env vars on Render

1. Go to your Render service → **Environment** tab.
2. Add each variable as a key/value pair.
3. Use Render's **Secret Files** feature for larger secrets if preferred.
4. Set `BASE_URL` to your Render URL, e.g. `https://your-app.onrender.com`.

---

## Upgrading to Redis FSM Storage

The default `MemoryStorage` loses bot conversation state on restart.
For production, switch to Redis:

```python
# app/bot_instance.py
from aiogram.fsm.storage.redis import RedisStorage

storage = RedisStorage.from_url(settings.redis_url)
dp = Dispatcher(storage=storage)
```

Set `REDIS_URL` in `.env` (e.g. `redis://localhost:6379/0` or your managed Redis URL on Railway/Render).

---

## Upgrading to PostgreSQL

Change `DATABASE_URL` to a PostgreSQL asyncpg URL:

```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

Install `asyncpg`:

```bash
pip install asyncpg
```

Railway and Render both offer one-click PostgreSQL databases.
After provisioning, copy the connection string into your env vars.

---

## Adding Real Products

Edit `app/seed.py` to replace the demo products with your real categories and listings.
Alternatively, build a product-management screen in the admin panel — the ORM models
are already wired up (`Category`, `Product`).

---

## Customising Bot Messages

All bot message text is in `app/templates/messages.py`.
Edit the strings there to match your brand, policies, and tone.
No code changes needed — just edit the text and restart the bot.

---

## Security Notes

- Never commit `.env` to Git.
- Use strong, unique values for all `*_SECRET` and `*_KEY` variables.
- The admin panel uses session-based login — not URL tokens.
- Admin pages have `Cache-Control: no-store` to prevent browser caching.
- The NOWPayments webhook verifies the HMAC-SHA512 signature on every request.
- Payment events are deduplicated to prevent double-processing.
- For production, consider Cloudflare Access or a VPN in front of `/admin/*`.
- See `SETUP_GUIDE.md` for `.onion` deployment instructions.
