import sys
import logging
import asyncio

from aiogram import Dispatcher

from bot.bot import bot
from bot.superadmin.handlers import router as superadmin_router
from bot.user.handlers import router as user_router
from bot.middleware import MediaGroupMiddleware
from bot.admin.handlers import router as admin_router
from bot.accountant.handlers import router as accountant_router
from bot.db.db import create_tables
import bot.db.default_db as default_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import bot.mailer as mailer


async def main():
    create_tables()
    default_db.create_start_db()
    dp = Dispatcher()
    dp.message.middleware(MediaGroupMiddleware())
    dp.include_router(superadmin_router)
    dp.include_router(admin_router)
    dp.include_router(accountant_router)
    dp.include_router(user_router)
    shed = AsyncIOScheduler(timezone='Europe/Moscow')
    shed.add_job(mailer.mailer, "cron", day=1, hour=0, minute=0)
    shed.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger("sqlalchemy.engine.Engine").disabled = True
    print("started!")
    try:
        asyncio.run(main())
    except Exception as exception:
        print(f"Exit! - {exception}")
