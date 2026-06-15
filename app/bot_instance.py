from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from app.routers.bot import router as bot_router

# NOTE: For production replace MemoryStorage with RedisStorage.
# See README.md — "Upgrading to Redis FSM Storage".
bot = Bot(token=settings.bot_token)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(bot_router)
