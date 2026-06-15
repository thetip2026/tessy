# Railway / Render — run both services as separate deployments (see SETUP_GUIDE.md)
# API service (set this as the start command for the web service):
web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000}

# Bot worker service (separate Railway/Render service, same repo):
# worker: python run_bot.py
