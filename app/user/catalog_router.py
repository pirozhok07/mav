
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F
from aiogram.filters import or_f, StateFilter
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from loguru import logger
from user.service import CallbackStateFilter, NavState
from sqlalchemy.ext.asyncio import AsyncSession
from config import bot, settings
from dao.dao import TasteDao, UserDAO, CategoryDao, ProductDao, PurchaseDao
from user.kbs import cancele_kb, main_user_kb, catalog_kb, product_kb, get_product_buy_kb, taste_kb
from user.schemas import PurchaseModel, TelegramIDModel, ProductCategoryIDModel, ItemCartData

catalog_router = Router()



@catalog_router.callback_query(F.data =="catalog")
async def page_catalog(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка каталога...")
    catalog_data = await CategoryDao.find_all(session=session_without_commit)
    # if catalog_data:                                  если нет каегорий
    #         await call.message.edit_text(
    #             text=f"В данной категории {count_products} товаров.",
    #             reply_markup=product_kb(product_data)
    await call.message.edit_text(
        text="Выберите категорию товаров:",
        reply_markup=catalog_kb(catalog_data)
    )

@catalog_router.callback_query(F.data.startswith('cart_'))
async def add_in_cart(call: CallbackQuery, session_with_commit: AsyncSession):
    await call.answer("Товар добавлен в корзину", show_alert=True)
    logger.error("i am here")
    _, product_id, taste_id = call.data.split('_')
    user_id = call.from_user.id
    purchase = await PurchaseDao.find_one_or_none(
        session=session_with_commit,
        filters=PurchaseModel(user_id=user_id,
                              status="NEW")
    )
    
    product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=product_id)
    await ProductDao.update_one_by_id(session=session_with_commit, data_id=product_id, in_cart=True)
    if taste_id != '0':
        await TasteDao.update_one_by_id(session=session_with_commit, data_id=taste_id, in_cart=True)
        taste = await TasteDao.find_one_or_none_by_id(session=session_with_commit, data_id=taste_id)
        add_text_data =f"{product.id}_{taste.id}"
    else: 
        add_text_data =f"{product.id}"
    
    
    if purchase is not None:
        text_data = f"{purchase.goods_id}, {add_text_data}"
        total_price = purchase.total + product.price
        await PurchaseDao.set_order(session=session_with_commit,
                                       data_id=purchase.id,
                                       goods=text_data,
                                       total=total_price)
                                       
    else:
        payment_data = {
            'user_id': int(user_id),
            'goods_id': add_text_data,
            'total': product.price,
            'status': 'NEW',
        }
        logger.error(payment_data)
        await PurchaseDao.add(session=session_with_commit, values=ItemCartData(**payment_data))

@catalog_router.callback_query(F.data.startswith('cart_'))
async def to_cart(call: CallbackQuery, session_with_commit: AsyncSession):
    await call.answer("Товар добавлен в корзину", show_alert=True)
    await add_in_cart(call, session_with_commit)
    await page_catalog(call, session_with_commit)

async def add_in_cart(call: CallbackQuery, session_with_commit: AsyncSession):
    _, product_id, taste_id = call.data.split('_')
    user_id = call.from_user.id
    purchase = await PurchaseDao.find_one_or_none(
        session=session_with_commit,
        filters=PurchaseModel(user_id=user_id,
                              status="NEW")
    )
    
    product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=product_id)
    await ProductDao.update_one_by_id(session=session_with_commit, data_id=product_id, in_cart=True)
    if taste_id != '0':
        await TasteDao.update_one_by_id(session=session_with_commit, data_id=taste_id, in_cart=True)
        taste = await TasteDao.find_one_or_none_by_id(session=session_with_commit, data_id=taste_id)
        add_text_data =f"{product.id}_{taste.id}"
    else: 
        add_text_data =f"{product.id}"
    
    
    if purchase is not None:
        text_data = f"{purchase.goods_id}, {add_text_data}"
        total_price = purchase.total + product.price
        await PurchaseDao.set_order(session=session_with_commit,
                                       data_id=purchase.id,
                                       goods=text_data,
                                       total=total_price)
                                       
    else:
        payment_data = {
            'user_id': int(user_id),
            'goods_id': add_text_data,
            'total': product.price,
            'status': 'NEW',
        }
        logger.error(payment_data)
        await PurchaseDao.add(session=session_with_commit, values=ItemCartData(**payment_data))
    


@catalog_router.callback_query(F.data.startswith("category_"))
async def page_catalog_products(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка товаров...")
    category_id = int(call.data.split("_")[-1])
    product_data = await ProductDao.get_products(session=session_without_commit, category_id=category_id)
    count_products = len(product_data)
    if count_products:
        await call.message.edit_text(
            text=f"В данной категории {count_products} товаров.",
            reply_markup=product_kb(product_data)
        )
    else:
        catalog_data = await CategoryDao.find_all(session=session_without_commit)
        await call.message.edit_text(text="В данной категории нет товаров.\n\n Выберите категорию товаров:", reply_markup=catalog_kb(catalog_data)) # возврат

@catalog_router.callback_query(F.data.startswith("taste_"))
async def show_taste(call: CallbackQuery, session_without_commit: AsyncSession):
    product_id = int(call.data.split("_")[-1]) 
    taste_data = await TasteDao.get_tastes(session=session_without_commit, product_id=product_id)
    if taste_data == []:
        # logger.error(call.data)data = 
        await call.answer("Товар добавлен в корзину", show_alert=True)
        new_call = CallbackQuery(
            id=call.id,
            from_user=call.from_user,
            chat_instance=call.chat_instance,
            data=f"cart_{str(product_id)}_0",
            message=call.message,
            inline_message_id=call.inline_message_id
        )
        await add_in_cart(new_call, session_without_commit)
        await page_catalog(call, session_without_commit)
        return
    await call.answer("Загрузка вкусов...") 
    product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id==product_id)  
    await call.message.edit_text(
        text="Выберите вкус:",
        reply_markup=taste_kb(taste_data, product.category_id))

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