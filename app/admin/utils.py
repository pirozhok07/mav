from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from admin.schemas import PurchaseForDellModel
from dao.dao import PurchaseDao
from config import bot
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings

async def process_dell_text_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get('last_msg_id')

    try:
        if last_msg_id:
            await bot.delete_message(chat_id=message.from_user.id, message_id=last_msg_id)
        else:
            logger.warning("Ошибка: Не удалось найти идентификатор последнего сообщения для удаления.")
        await message.delete()

    except Exception as e:
        logger.error(f"Произошла ошибка при удалении сообщения: {str(e)}")

 

async def scheduled_cleanup(session_with_commit: AsyncSession):
    """Запланированная очистка БД"""
    
    for admin_id in settings.ADMIN_IDS:
        try:
            logger.info("🚀 Запуск ежедневной очистки БД")
            await PurchaseDao.delete(session=session_with_commit, 
                                     filters=PurchaseForDellModel(status="NEW"))
            logger.info("✅ Очистка БД завершена")

            # Уведомление администратору
            await bot.send_message(
                chat_id=admin_id,
                text=f"✅ Ежедневная очистка БД выполнена\nВремя: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
        except Exception as e:
            error_msg = f"❌ Ошибка при очистке БД: {e}"
            logger.error(error_msg)
            await bot.send_message(admin_id, error_msg)