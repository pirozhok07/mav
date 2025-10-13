from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import bot

hello_router = Router()

@hello_router.message(Command(commands=["remind"]))
# middleware просовывает для нас sheduler в аргументы функции 
async def hello(message:Message, bot: Bot, scheduler: AsyncIOScheduler):
    # получаем id, обратившегося к боту
    id = message.from_user.id
    await message.answer(
        text="Бот будет напоминать каждые 20 секунд и каждый день в 1.10"
    )
    # задаём выполнение задачи в равные промежутки времени
    scheduler.add_job(bot.send_message,'interval',seconds=20 ,args=(id,"Я напоминаю каждые 20 секунд"))
    # задаём выполнение задачи по cron - гибкий способ задавать расписание. Подробнеее https://crontab.guru/#8_*_*_4
    scheduler.add_job(bot.send_message,'cron',hour=1,minute=10,args=(id,"Я напомнил в 1.10 по Москве"))