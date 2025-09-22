from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from dao.dao import UserDAO, ProductDao, PurchaseDao
from user.kbs import cart_kb, dell_cart_kb, main_user_kb, purchases_kb
from user.schemas import PurchaseIDModel, TelegramIDModel, UserModel, CartModel

cart_router = Router()

@cart_router.callback_query(F.data == "cart")
async def page_user_cart(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Моя корзина")

    # Получаем список покупок пользователя
    # cart = await ProductDao.find_all(session=session_without_commit,
                                                #   filters=CartModel(id=call.from_user.id))
    # count_products = len(products_category)
    purchases = await UserDAO.get_cart(session=session_without_commit, telegram_id=call.from_user.id)
    logger.error(purchases)
    if not purchases:
        await call.message.edit_text(
            text=f"🔍 <b>У вас пока нет покупок.</b>\n\n"
                 f"Откройте каталог и выберите что-нибудь интересное!",
            reply_markup=main_user_kb(call.from_user.id)
        )
        return
    product_text = (
            f"🛒 <b>Информация о вашей корзине:</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n")
    cart_total=0
    # Для каждой покупки отправляем информацию
    for purchase in purchases:

        logger.error(purchase)
        product = purchase.product
        logger.error(product)
        # file_text = "📦 <b>Товар включает файл:</b>" if product.file_id else "📄 <b>Товар не включает файлы:</b>"

        product_text += (
            f"🔹 {product.name} - {product.price} ₽\n"
        )
        cart_total +=product.price
    product_text += (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"сумма заказа: {cart_total}₽\n")

    await call.message.edit_text(
        text=product_text,
        reply_markup=cart_kb()
    )

@cart_router.callback_query(F.data == 'edit_cart')
async def edit_cart(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим редактирования корзины')
    all_items = await UserDAO.get_cart(session=session_without_commit, telegram_id=call.from_user.id)

    for item in all_items:
        product = item.product
        product_text = (f'🛒 Описание товара:\n\n'
                        f'🔹 <b>Название товара:</b> <b>{product.name}</b>\n'
                        f'🔹 <b>Описание:</b>\n\n<b>{product.description}</b>\n\n'
                        f'🔹 <b>Цена:</b> <b>{product.price} ₽</b>\n'
                        f'🔹 <b>Описание (закрытое):</b>\n\n<b>{product.hidden_content}</b>\n\n')
        await call.message.answer(text=product_text, reply_markup=dell_cart_kb(product.id))
    # await call.message.answer("--", reply_markup=)

@cart_router.callback_query(F.data.startswith('dell_item_'))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    item_id = int(call.data.split('_')[-1])
    await PurchaseDao.delete(session=session_with_commit, filters=PurchaseIDModel(id=item_id))
    await call.message.edit_text(f"Товар с ID {item_id} удален!", show_alert=True)
    await call.message.delete()