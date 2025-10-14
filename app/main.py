import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from config import bot, admins, dp
from dao.database_middleware import DatabaseMiddlewareWithoutCommit, DatabaseMiddlewareWithCommit, SchedulerMiddleware
from admin.hello import clear_db_table
from admin.admin import admin_router
from user.user_router import user_router
from user.cart_router import cart_router
from user.catalog_router import catalog_router

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()
# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

# Функция, которая выполнится, когда бот запустится
async def start_bot():
    scheduler.add_job(
        clear_db_table,
        CronTrigger(hour=11, minute=39, timezone="Europe/Moscow"),
        args=(bot, 1330085937),
        kwargs={"text": "text"},
        id="daily_mess"
    )
    scheduler.start()
    await set_commands()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass
    logger.info("Бот успешно запущен.")

# Функция, которая выполнится, когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except:
        pass
    logger.error("Бот остановлен!")


async def main():
    # scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    # scheduler.start()
    # Регистрация мидлварей
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())
    # dp.update.middleware(SchedulerMiddleware(scheduler=scheduler)())

    # Регистрация роутеров
    dp.include_router(catalog_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(cart_router)
    # dp.include_router(hello_router)

    # Регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # Запуск бота в режиме long polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())