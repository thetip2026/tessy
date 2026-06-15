# Step-by-Step Setup & Deployment Guide

This guide covers everything from first-time local setup to production deployment
on Railway, and finally how to put the admin panel on a Tor `.onion` address.

---

## Part 1 — Local Setup (Start Here)

### Step 1: Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot`.
3. Enter a display name (e.g. `My Shop`).
4. Enter a username ending in `bot` (e.g. `myshop_bot`).
5. BotFather will give you a token — copy it.

### Step 2: Set Up the Project

```bash
cd telegram-crypto-bot
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` in a text editor and fill in:

| Value | Where to get it |
|---|---|
| `BOT_TOKEN` | From BotFather in Step 1 |
| `BOT_USERNAME` | The `@username_bot` you chose |
| `BASE_URL` | Your public HTTPS URL (Railway/Render later) |
| `ADMIN_CHAT_IDS` | Your Telegram numeric ID — send `/start` to @userinfobot |
| `ADMIN_API_KEY` | Run: `openssl rand -hex 32` |
| `ADMIN_USERNAME` | Choose a username for the admin panel |
| `ADMIN_PASSWORD` | Choose a strong password |
| `SESSION_SECRET` | Run: `openssl rand -hex 32` |
| `WEBHOOK_SECRET` | Run: `openssl rand -hex 32` |
| `NOWPAYMENTS_API_KEY` | From nowpayments.io dashboard |
| `NOWPAYMENTS_IPN_SECRET` | From nowpayments.io IPN settings |

For local testing set:
```
SECURE_COOKIES=false
DATABASE_URL=sqlite+aiosqlite:///./bot.db
```

### Step 4: Start the API Server

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/health` — expect `{"ok": true}`.
Open `http://127.0.0.1:8000/admin/login` — log in with your admin credentials.

### Step 5: Start the Bot

Open a **second terminal**, activate the same venv, then:

```bash
python run_bot.py
```

In Telegram, send `/start` to your bot. You should see the main menu.

### Step 6: Configure NOWPayments IPN

1. Log in to [nowpayments.io](https://nowpayments.io).
2. Go to **Payment settings → IPN**.
3. Set IPN URL to: `https://YOUR-DOMAIN/webhooks/nowpayments`
   (Use `BASE_URL` from your `.env`)
4. Copy the IPN secret into `NOWPAYMENTS_IPN_SECRET` in your `.env`.
5. Copy your API key into `NOWPAYMENTS_API_KEY`.

### Step 7: Test the Full Flow

1. `GET /health` returns `{"ok": true}`.
2. `/start` in Telegram shows the shop menu.
3. Browse Listings → add item → view Cart.
4. Set delivery address and payment method.
5. Click Checkout → payment address and amount appear in Telegram.
6. Log in to `/admin/login` and view the order.
7. (Optional) Send a tiny real NOWPayments test payment to verify webhook updates.

---

## Part 2 — Railway Deployment (Recommended)

Railway runs both the FastAPI API and the bot polling process as persistent services.

### Step 1: Push to GitHub

```bash
cd telegram-crypto-bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy the API Service

1. Go to [railway.com](https://railway.com) and sign in with GitHub.
2. Click **New Project → Deploy from GitHub repo**.
3. Select your repository.
4. Set the **Start command**:
   ```
   uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000}
   ```
5. Railway will auto-detect Python from `requirements.txt`.

### Step 3: Add Environment Variables

In the Railway service → **Variables** tab, add all keys from `.env.example`.
Set `SECURE_COOKIES=true`.

### Step 4: Get Your Public URL

In the service → **Settings → Networking**, click **Generate Domain**.
Copy the URL (e.g. `https://your-bot.up.railway.app`).
Update `BASE_URL` in Railway vars to this URL.

Your API is now live. Test:
- `https://your-bot.up.railway.app/health`
- `https://your-bot.up.railway.app/admin/login`

### Step 5: Deploy the Bot Worker

1. In the same Railway project, click **New → Service → From GitHub repo**.
2. Select the same repository.
3. Set the **Start command**:
   ```
   python run_bot.py
   ```
4. Add the same environment variables (especially `BOT_TOKEN`).

Railway now keeps both processes running and restarts them automatically.

### Step 6: Set NOWPayments IPN URL

In NOWPayments dashboard → IPN settings:
```
https://your-bot.up.railway.app/webhooks/nowpayments
```

---

## Part 3 — Render Deployment (Alternative)

### API Service

1. Go to [render.com](https://render.com) → **New → Web Service**.
2. Connect your GitHub repo.
3. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host=0.0.0.0 --port=$PORT`
4. Add all environment variables in the **Environment** tab.
5. Set `BASE_URL` to your Render URL (e.g. `https://your-app.onrender.com`).

### Bot Worker

1. **New → Background Worker**.
2. Same repo, same env vars.
3. Start command: `python run_bot.py`

> **Render free tier spins down after inactivity.** Use a paid plan for a production bot
> to avoid the polling process stopping.

---

## Part 4 — Admin Panel on a Tor `.onion` Address

This puts your admin panel behind a Tor onion service so it is only reachable
via Tor Browser, removing public DNS exposure entirely.

The Telegram bot continues to run normally — only the admin UI goes behind Tor.

### Prerequisites

- A Linux server (Ubuntu/Debian recommended) or VPS.
- Your FastAPI app already running locally on `127.0.0.1:8000`.

### Step 1: Install Tor

```bash
sudo apt update
sudo apt install tor -y
```

### Step 2: Configure the Onion Service

Edit `/etc/tor/torrc`:

```bash
sudo nano /etc/tor/torrc
```

Add these lines at the end of the file:

```
HiddenServiceDir /var/lib/tor/bot_admin/
HiddenServiceVersion 3
HiddenServicePort 80 127.0.0.1:8000
```

> `HiddenServiceVersion 3` gives you a modern v3 onion address (56 characters).
> v3 is more secure and the current standard.

### Step 3: Restart Tor and Get Your Onion Address

```bash
sudo systemctl restart tor
sudo cat /var/lib/tor/bot_admin/hostname
```

Tor will print your `.onion` address, e.g.:
```
abcdef1234567890abcdef1234567890abcdef1234567890abcdef.onion
```

### Step 4: Access the Admin Panel

1. Open **Tor Browser** (download from [torproject.org](https://www.torproject.org)).
2. Navigate to `http://YOUR_ONION_ADDRESS.onion/admin/login`.
3. Log in with your admin credentials.

### Step 5: (Recommended) Enable Client Authorization

Client authorization adds a credential check before Tor even forwards
the request to your app — an extra layer on top of the login form.

```bash
sudo mkdir -p /var/lib/tor/bot_admin/authorized_clients
```

Generate a key pair on your client machine:
```bash
# Install basez if not available
sudo apt install basez -y

# Generate a Curve25519 key pair
openssl genpkey -algorithm X25519 -out admin_onion.key
openssl pkey -in admin_onion.key -pubout | tail -n +2 | head -n -1 | base64 -d | basez --base32 | tr '=' '\0' > admin_onion.pub
```

Create an authorized client file on the server:
```bash
echo "descriptor:x25519:$(cat admin_onion.pub)" | sudo tee /var/lib/tor/bot_admin/authorized_clients/admin.auth
sudo systemctl restart tor
```

Now only Tor Browser with the matching private key can reach your onion service.

### Step 6: Keep the Public Webhook Reachable

If you are also running the bot and NOWPayments webhooks on the same server,
keep those on your normal public domain (e.g. via Nginx on port 443).
Only route `/admin/*` through Tor — or run two separate app instances:
- Public: `127.0.0.1:8000` for webhooks (exposed via Nginx/Certbot to the internet)
- Onion: `127.0.0.1:8001` for admin (Tor forwards port 80 → 127.0.0.1:8001)

To run a second FastAPI instance on port 8001:
```bash
uvicorn app.main:app --host=127.0.0.1 --port=8001
```
Then in `torrc`:
```
HiddenServicePort 80 127.0.0.1:8001
```

### Security Checklist for Onion Deployment

- [ ] `SECURE_COOKIES=false` when admin is accessed over HTTP via Tor (no TLS needed — Tor encrypts the connection)
- [ ] Strong `ADMIN_PASSWORD` (12+ chars, symbols)
- [ ] `SESSION_SECRET` is long and random
- [ ] Tor hidden service directory owned by `debian-tor` user only
- [ ] Keep Tor updated: `sudo apt upgrade tor`
- [ ] Do not expose `/admin/*` on the public internet — Nginx should block those routes
- [ ] Consider client authorization (Step 5 above) for maximum protection

---

## Part 5 — Nginx Reverse Proxy (Optional, for Public Webhook)

If you want Nginx in front of FastAPI on a public domain while keeping the admin onion-only:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.example;

    ssl_certificate     /etc/letsencrypt/live/your-domain.example/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.example/privkey.pem;

    # Block public access to admin
    location /admin {
        return 403;
    }

    # Allow webhooks and health check publicly
    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

Get a free TLS certificate with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.example
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `BOT_TOKEN not found` | Check `.env` has `BOT_TOKEN=` with no spaces around `=` |
| `/health` returns 500 | Check terminal for Python error — usually a missing `.env` value |
| Admin login fails | Double-check `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env` |
| Webhook not firing | Make sure `BASE_URL` is your real HTTPS URL, not `localhost` |
| Payment address blank | NOWPayments API key or currency settings incorrect |
| Bot not responding | `run_bot.py` is not running, or `BOT_TOKEN` is wrong |
| Onion not loading | Tor not running (`sudo systemctl status tor`) or wrong `hostname` file |

For any error, paste the exact terminal output and open an issue or continue the conversation.
