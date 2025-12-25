import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.config import TOKEN
from app import chat, onboarding, total_info
from app.handlers.file.doc import sample, one_day, image
from app.handlers import start_hd, admin
from app.storage.models import async_main

# ====================== Логирование ======================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== Создаем бота и диспетчер ======================
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ====================== Startup ======================
async def on_startup():
    """
    Функция, выполняемая при запуске бота
    """
    logger.info("🤖 Бот запускается...")

    # Восстанавливаем расписания опросов
    await onboarding.restore_schedules(bot)

    logger.info("✅ Расписания опросов восстановлены")
    logger.info("✅ Бот готов к работе!")

# ====================== Основная функция ======================
async def main():
    # Инициализация базы данных
    await async_main()

    # Регистрируем хэндлеры
    dp.include_routers(
        start_hd.router,
        admin.router,
        chat.router,
        sample.router,
        total_info.router,
        one_day.router,
        image.router,
        onboarding.router
    )

    # Регистрируем startup hook
    dp.startup.register(on_startup)

    # Старт бота
    logger.info("🤖 Бот запущен...")
    await dp.start_polling(bot)

# ====================== Точка входа ======================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот выключен!")