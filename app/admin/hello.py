from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger
from admin.schemas import PurchaseForDellModel
from dao.dao import PurchaseDao
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from config import bot


async def clear_db_table(bot: Bot, chat_id: int, text: str, session_with_commit: AsyncSession):
    try:
        await PurchaseDao.delete(session=session_with_commit,
                                 filters=PurchaseForDellModel(status="NEW",
                                                              created_at=d
                                 ))
    except Exception as e:
        logger.error("ошибка смс по таймеру")