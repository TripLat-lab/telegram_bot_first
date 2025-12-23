import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.config import TOKEN

from app import chat, onboarding,total_info
from app.handlers.file.doc import sample, one_day, image
from app.handlers import start_hd,admin
from app.storage.models import async_main

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    await async_main()
    dp.include_routers(start_hd.router, admin.router, chat.router,
                       sample.router, total_info.router, one_day.router, image.router, onboarding.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO)
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Выключен!")