from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from config import bot, settings
from dao.dao import TasteDao, UserDAO, CategoryDao, ProductDao, PurchaseDao
from user.kbs import cancele_kb, main_user_kb, catalog_kb, product_kb, get_product_buy_kb, taste_kb
from user.schemas import TasteProductIDModel, TelegramIDModel, ProductCategoryIDModel, ItemCartData

catalog_router = Router()

@catalog_router.callback_query(F.data == "catalog")
async def page_catalog(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка каталога...")
    catalog_data = await CategoryDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text="Выберите категорию товаров:",
        reply_markup=catalog_kb(catalog_data)
    )

@catalog_router.callback_query(F.data.startswith("category_"))
async def page_catalog_products(call: CallbackQuery, session_without_commit: AsyncSession):
    category_id = int(call.data.split("_")[-1])
    product_data = await ProductDao.get_cart(session=session_without_commit, telegram_id=call.from_user.id)
    product_data = await ProductDao.find_one_or_none(session=session_without_commit,
                                                  filters=ProductCategoryIDModel(category_id=category_id, quantity=))
    count_products = len(product_data)
    if count_products:
        await call.message.edit_text(
            text=f"В данной категории {count_products} товаров.",
            reply_markup=product_kb(product_data)
        )
        # for product in products_category:
        #     product_text = (
        #         f"📦 <b>Название товара:</b> {product.name}\n\n"
        #         f"💰 <b>Цена:</b> {product.price} руб.\n\n"
        #         f"📝 <b>Описание:</b>\n<i>{product.description}</i>\n\n"
        #         f"━━━━━━━━━━━━━━━━━━"
        #     )
        #     if product.category_id == 1:
        #         await call.message.answer(
        #             product_text,
        #             reply_markup=product_kb_1(product.id)
        #         )
        #     else:
        #         await call.message.answer(
        #             product_text,
        #             reply_markup=product_kb(product.id)
        #         )
            
        # await call.message.answer(".", reply_markup=cancele_kb())
    else:
        catalog_data = await CategoryDao.find_all(session=session_without_commit)
        await call.message.edit_text(text="В данной категории нет товаров.\n\n Выберите категорию товаров:", reply_markup=catalog_kb(catalog_data)) # возврат

@catalog_router.callback_query(F.data.startswith("taste_"))
async def show_taste(call: CallbackQuery, session_without_commit: AsyncSession):
    product_id = int(call.data.split("_")[-1])    
    taste_data = await TasteDao.find_all(session=session_without_commit, filters=TasteProductIDModel(product_id=product_id))
    await call.message.edit_text(
        text="Выберите вкус:",
        reply_markup=taste_kb(taste_data))
    
    # count_tastes = len(tastes_product)
    # if count_tastes:

    #     await call.message.edit_text(f"У данного товара {count_tastes} вкусов.")
    #     for taste in tastes_product:
    #         taste_text = (
    #             f"📦 <b>Название вкуса:</b> {taste.taste_name}\n\n"
    #             f"━━━━━━━━━━━━━━━━━━"
    #         )
    #         await call.message.answer(
    #             taste_text,
    #             reply_markup=taste_kb(taste.id)
    #         )
    #     await call.message.answer("-----", reply_markup=cancele_kb())
    # else:
    #     await call.message.edit_text(text="В данной категории нет товаров.\n\n Выберите категорию товаров:") # возврат   
# @catalog_router.callback_query(F.data.startswith('cart_'))
# async def process_about(call: CallbackQuery, session_without_commit: AsyncSession):
    # user_info = await UserDAO.find_one_or_none(
    #     session=session_without_commit,
    #     filters=TelegramIDModel(telegram_id=call.from_user.id)
    # )
    # _, product_id, price = call.data.split('_')
#     await bot.send_invoice(
#         chat_id=call.from_user.id,
#         title=f'Оплата 👉 {price}₽',
#         description=f'Пожалуйста, завершите оплату в размере {price}₽, чтобы открыть доступ к выбранному товару.',
#         payload=f"{user_info.id}_{product_id}",
#         provider_token=settings.PROVIDER_TOKEN,
#         currency='rub',
#         prices=[LabeledPrice(
#             label=f'Оплата {price}',
#             amount=int(price) * 100
#         )],
#         reply_markup=get_product_buy_kb(price)
#     )
#     await call.message.delete()

@catalog_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)




# @catalog_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
# async def add_in_cart(message: Message, session_with_commit: AsyncSession):
#     payment_info = message.successful_payment
#     user_id, product_id = payment_info.invoice_payload.split('_')
#     payment_data = {
#         'user_id': int(user_id),
#         'payment_id': payment_info.telegram_payment_charge_id,
#         'price': payment_info.total_amount / 100,
#         'product_id': int(product_id)
#     }
#     # Добавляем информацию о покупке в базу данных
#     await PurchaseDao.add(session=session_with_commit, values=PaymentData(**payment_data))
#     product_data = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=int(product_id))

#     # Формируем уведомление администраторам
#     for admin_id in settings.ADMIN_IDS:
#         try:
#             username = message.from_user.username
#             user_info = f"@{username} ({message.from_user.id})" if username else f"c ID {message.from_user.id}"

#             await bot.send_message(
#                 chat_id=admin_id,
#                 text=(
#                     f"💲 Пользователь {user_info} купил товар <b>{product_data.name}</b> (ID: {product_id}) "
#                     f"за <b>{product_data.price} ₽</b>."
#                 )
#             )
#         except Exception as e:
#             logger.error(f"Ошибка при отправке уведомления администраторам: {e}")

#     # Подготавливаем текст для пользователя
#     file_text = "📦 <b>Товар включает файл:</b>" if product_data.file_id else "📄 <b>Товар не включает файлы:</b>"
#     product_text = (
#         f"🎉 <b>Спасибо за покупку!</b>\n\n"
#         f"🛒 <b>Информация о вашем товаре:</b>\n"
#         f"━━━━━━━━━━━━━━━━━━\n"
#         f"🔹 <b>Название:</b> <b>{product_data.name}</b>\n"
#         f"🔹 <b>Описание:</b>\n<i>{product_data.description}</i>\n"
#         f"🔹 <b>Цена:</b> <b>{product_data.price} ₽</b>\n"
#         f"🔹 <b>Закрытое описание:</b>\n<i>{product_data.hidden_content}</i>\n"
#         f"━━━━━━━━━━━━━━━━━━\n"
#         f"{file_text}\n\n"
#         f"ℹ️ <b>Информацию о всех ваших покупках вы можете найти в личном профиле.</b>"
#     )

#     # Отправляем информацию о товаре пользователю
#     if product_data.file_id:
#         await message.answer_document(
#             document=product_data.file_id,
#             caption=product_text,
#             reply_markup=main_user_kb(message.from_user.id)
#         )
#     else:
#         await message.edit_text(
#             text=product_text,
#             reply_markup=main_user_kb(message.from_user.id)
#         )