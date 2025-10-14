from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import bot


async def clear_db_table(bot: Bot, chat_id: int, text: str):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.error("ошибка смс по таймеру")