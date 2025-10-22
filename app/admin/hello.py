from datetime import date, datetime, time
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger
from admin.schemas import DeliveryDate, PurchaseForDellModel
from dao.dao import DeliveryTimeDao, PurchaseDao
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from dao.database import async_session_maker

from config import bot


async def clear_db_table(bot: Bot, chat_id: int, text: str):
    async with async_session_maker() as db_session:
        # try:
        #     await PurchaseDao.delete(session=db_session,
        #                              filters=PurchaseForDellModel(status="NEW")
        #                              )
        #     await db_session.commit()
        #     await bot.send_message(chat_id=1330085937, text=text)
        #     logger.error(" смс по таймеру")
        # except Exception as e:
        #     await db_session.rollback()
        #     logger.error(f"ошибка смс по таймеру {e}")

        try:
            await DeliveryTimeDao.add(session=db_session, values=DeliveryDate(date=date.today(),
                                                                              time=time(19, 30)))
            await db_session.commit()
            await bot.send_message(chat_id=1330085937, text=text)
            logger.error(" время установлено по таймеру")
        except Exception as e:
            await db_session.rollback()
            logger.error(f"ошибка установленного времени по таймеру {e}")