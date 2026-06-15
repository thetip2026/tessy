"""
Bot process entry point.
Run this in a SEPARATE terminal / service from the FastAPI server:
    python run_bot.py

This process uses long polling to receive Telegram messages.
It does NOT need a public URL — polling works from behind NAT.
"""
import asyncio
from aiogram.types import BotCommand
from app.bot_instance import bot, dp


async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Open the shop"),
    ])
    print("Bot is running (polling)... Ctrl+C to stop.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
