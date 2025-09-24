from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from dao.dao import TasteDao, UserDAO, ProductDao, PurchaseDao
from user.kbs import cart_kb, dell_cart_kb, main_user_kb, purchases_kb
from user.schemas import ItemCartData, ProductIDModel, PurchaseIDModel, TasteIDModel, TelegramIDModel, UserModel, CartModel

cart_router = Router()

# @cart_router.callback_query(F.data.startswith('taste_cart_'))
# async def add_in_cart_taste(call: CallbackQuery, session_with_commit: AsyncSession):
#     user_info = await UserDAO.find_one_or_none(
#         session=session_with_commit,
#         filters=TelegramIDModel(telegram_id=call.from_user.id)
#     )
#     _, taste_id = call.data.split('_')
#     taste_info = await TasteDao.find_one_or_none(
#         session=session_with_commit,
#         filters=TasteIDModel(id=taste_id)
#     )
#     product_id = await ProductDao.find_one_or_none(
#         session=session_with_commit,
#         filters=ProductIDModel(id=taste_info.product_id)
#     )
#     user_id = call.from_user.id
#     payment_data = {
#         'user_id': user_id,
#         'product_id': int(product_id),
#         #taste
#         'status': 'NEW',
#     }
#     logger.error(payment_data)
#     # Добавляем информацию о покупке в базу данных
#     await PurchaseDao.add(session=session_with_commit, values=ItemCartData(**payment_data))

@cart_router.callback_query(F.data.startswith('ctaste_'))
async def add_in_cart_taste(call: CallbackQuery, session_with_commit: AsyncSession):
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=call.from_user.id)
    )
    _, taste_id = call.data.split('_')
    taste_info = await TasteDao.find_one_or_none(
        session=session_with_commit,
        filters=TasteIDModel(id=taste_id)
    )
    product_info = await ProductDao.find_one_or_none(
        session=session_with_commit,
        filters=ProductIDModel(id=taste_info.product_id)
    )
    product_id = product_info.id
    user_id = call.from_user.id
    payment_data = {
        'user_id': user_id,
        'product_id': int(product_id),
        #taste
        'status': 'NEW',
    }
    logger.error(payment_data)
    # Добавляем информацию о покупке в базу данных
    await PurchaseDao.add(session=session_with_commit, values=ItemCartData(**payment_data))

# @catalog_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
@cart_router.callback_query(F.data.startswith('cart_'))
async def add_in_cart(call: CallbackQuery, session_with_commit: AsyncSession):
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=call.from_user.id)
    )
    _, product_id, taste_id = call.data.split('_')
    user_id = call.from_user.id
    logger.error(taste_id)
    payment_data = {
        'user_id': user_id,
        'product_id': int(product_id),
        #taste
        'status': 'NEW',
    }
    logger.error(payment_data)
    # Добавляем информацию о покупке в базу данных
    await PurchaseDao.add(session=session_with_commit, values=ItemCartData(**payment_data))
    # product_data = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=int(product_id))

    # # Формируем уведомление администраторам
    # for admin_id in settings.ADMIN_IDS:
    #     try:
    #         username = message.from_user.username
    #         user_info = f"@{username} ({message.from_user.id})" if username else f"c ID {message.from_user.id}"

    #         await bot.send_message(
    #             chat_id=admin_id,
    #             text=(
    #                 f"💲 Пользователь {user_info} купил товар <b>{product_data.name}</b> (ID: {product_id}) "
    #                 f"за <b>{product_data.price} ₽</b>."
    #             )
    #         )
    #     except Exception as e:
    #         logger.error(f"Ошибка при отправке уведомления администраторам: {e}")

    # # Подготавливаем текст для пользователя
    # file_text = "📦 <b>Товар включает файл:</b>" if product_data.file_id else "📄 <b>Товар не включает файлы:</b>"
    # product_text = (
    #     f"🎉 <b>Спасибо за покупку!</b>\n\n"
    #     f"🛒 <b>Информация о вашем товаре:</b>\n"
    #     f"━━━━━━━━━━━━━━━━━━\n"
    #     f"🔹 <b>Название:</b> <b>{product_data.name}</b>\n"
    #     f"🔹 <b>Описание:</b>\n<i>{product_data.description}</i>\n"
    #     f"🔹 <b>Цена:</b> <b>{product_data.price} ₽</b>\n"
    #     f"🔹 <b>Закрытое описание:</b>\n<i>{product_data.hidden_content}</i>\n"
    #     f"━━━━━━━━━━━━━━━━━━\n"
    #     f"{file_text}\n\n"
    #     f"ℹ️ <b>Информацию о всех ваших покупках вы можете найти в личном профиле.</b>"
    # )

    # # Отправляем информацию о товаре пользователю
    # if product_data.file_id:
    #     await message.answer_document(
    #         document=product_data.file_id,
    #         caption=product_text,
    #         reply_markup=main_user_kb(message.from_user.id)
    #     )
    # else:
    #     await message.edit_text(
    #         text=product_text,
    #         reply_markup=main_user_kb(message.from_user.id)
    #     )

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
                        f'🔹 <b>Цена:</b> <b>{product.price} ₽</b>\n')
        await call.message.answer(text=product_text, reply_markup=dell_cart_kb(product.id))
    # await call.message.answer("--", reply_markup=)

@cart_router.callback_query(F.data.startswith('item_dell_'))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    item_id = int(call.data.split('_')[-1])
    await PurchaseDao.delete(session=session_with_commit, filters=PurchaseIDModel(id=item_id))
    await call.message.edit_text(f"Товар с ID {item_id} удален!", show_alert=True)
    await call.message.delete()