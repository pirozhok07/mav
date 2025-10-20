from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from loguru import logger
from admin.kbs import admin_accept_kb
from user.user_router import page_home
from user.catalog_router import page_catalog
from user.service import NavState
from sqlalchemy.ext.asyncio import AsyncSession
from dao.dao import TasteDao, UserDAO, ProductDao, PurchaseDao
from user.kbs import cancele_kb, cart_kb, date_kb, delete_kb, main_user_kb, order_kb, purchases_kb
from user.schemas import ItemCartData, ProductIDModel, ProductUpdateIDModel, PurchaseIDModel, PurchaseModel, TasteIDModel, TelegramIDModel, UserModel, CartModel
from config import bot, settings
from datetime import date, datetime

cart_router = Router()

class DoOrder(StatesGroup):
    adress = State()
    date = State()




@cart_router.callback_query(F.data == 'edit_cart')
async def edit_cart(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим редактирования корзины')

    user_id = call.from_user.id
    purchase = await PurchaseDao.find_one_or_none(
        session=session_without_commit,
        filters=PurchaseModel(user_id=user_id,
                              status="NEW")
    )
    purchases = purchase.goods_id.split(', ')
    product_data=[] 
    taste_data=[]
    for good in purchases:
        if good.find('_') != -1:
            product_id, taste_id = good.split('_')
            taste = await TasteDao.find_one_or_none_by_id(session=session_without_commit, data_id=taste_id)
            product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=product_id)
        else: 
            taste=None
            product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=good)
        product_data.append(product)
        taste_data.append(taste)
    
    await call.message.edit_text(
        text="Выберите товар для удаления:",
        reply_markup=delete_kb(product_data, taste_data))
    
@cart_router.callback_query(F.data == 'clean_cart')
async def clean_cart(call: CallbackQuery, session_with_commit: AsyncSession):
    await call.answer('Корзина очищена', show_alert=True)

    user_id = call.from_user.id
    await PurchaseDao.deleteAll(session=session_with_commit)
    await page_home(call)
    

@cart_router.callback_query(F.data.startswith('itemDell_'))
async def dell_item(call: CallbackQuery, session_with_commit: AsyncSession):
    await call.answer("Товар удален из корзины", show_alert=True)
    _, product_id, taste_id = call.data.split('_')
    await ProductDao.update_one_by_id(session=session_with_commit, data_id=product_id, in_cart=False)
    dell_text=product_id
    if taste_id != "0":
        await TasteDao.update_one_by_id(session=session_with_commit, data_id=taste_id, in_cart=False)
        dell_text +=f"_{taste_id}"
    purchase = await PurchaseDao.find_one_or_none(
        session=session_with_commit,
        filters=PurchaseModel(user_id=call.from_user.id,
                              status="NEW")
    )
    goods = purchase.goods_id.split(', ')   
    goods.remove(dell_text)
    product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=product_id)
    new_total=purchase.total-product.price
    await PurchaseDao.set_order(session_with_commit, data_id=purchase.id, goods=', '.join(goods), total=new_total)
    await edit_cart(call, session_with_commit)

@cart_router.callback_query(F.data == 'do_order')
async def get_adress(call: CallbackQuery, state: FSMContext):
    await call.answer("Оформление заказа")
    # await call.message.answer(f"Заказ будет доставлен ориентировочно сегодня после 19:30")
    msg = await call.message.edit_text(text="Куда доставить ваш заказ? ", reply_markup=cancele_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(DoOrder.adress)

@cart_router.callback_query(F.text, DoOrder.adress)
async def get_date(message: Message, state: FSMContext):
    # await call.message.answer(f"Заказ будет доставлен ориентировочно сегодня после 19:30")
    await state.update_data(adress=message.text)
    logger.error("get_date")
    msg = await message.edit_text(text="Укажите дату доставки: ", reply_markup=date_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(DoOrder.date)

@cart_router.message(F.data.startswith("get_date_"), DoOrder.date)
async def create_order(call: CallbackQuery, session_with_commit: AsyncSession, state: FSMContext):
    
    logger.error("create_order")
    date = call.data.split("_")[-1]
    await state.update_data(date = date)
    await state.update_data(adress=call.message.text)
    order = await state.get_data()
    await bot.delete_message(chat_id=call.message.from_user.id, message_id=call.message.message_id)
    await bot.delete_message(chat_id=call.message.from_user.id, message_id=order["last_msg_id"])

    purchase = await PurchaseDao.find_one_or_none(
        session=session_with_commit,
        filters=PurchaseModel(user_id=call.message.from_user.id,
                              status="NEW")
    )
    order = await state.get_data()
    await PurchaseDao.set_order(session_with_commit, data_id=purchase.id, getdate=order["date"], adress=order["adress"], status="WAIT", money=1)
    await state.clear()

    if purchase.total < 500 : total=purchase.total+50
    await call.answer(f"Оплата переводом.\n Итого: {total}₽\nРЕКВИЗИТЫ\nСпасибо за заказ\nКурьер напишет вам за 15 мин", show_alert=True)
    money_text = f"Оплата переводом.\n"
    
    await page_home(call)
    product_text=""
    purchases = purchase.goods_id.split(', ')
    for good in purchases:
        if good.find('_') != -1:
            product_id, taste_id = good.split('_')
            taste = await TasteDao.find_one_or_none_by_id(session=session_with_commit, data_id=taste_id)
            product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=product_id)
            product_text += (f"🔹 {product.name} ({taste.taste_name})\n")
        else: 
            product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=good)
            product_text += (f"🔹 {product.name}\n")
        
    username = call.from_user.username
    user_info = f"@{username}" if username else f"c ID {call.from_user.id}"
    for admin_id in settings.ADMIN_IDS:
        try:
            
            await bot.send_message(
                chat_id=admin_id,
                text=(
                    f"💲 Пользователь {user_info} оформил заказ\n"
                    f"-------------------------------------------\n"
                    f"{product_text}"
                    f"за <b>{purchase.total} ₽</b> {money_text}"
                    f"дата: {purchase.date}\n"
                    f"адресс: {purchase.adress}\n"
                ), reply_markup=admin_accept_kb(user_id=call.from_user.id)
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администраторам: {e}")

# @cart_router.message(F.text, DoOrder.adress)
# async def get_adress(message: Message, state: FSMContext):
#     await state.update_data(adress=message.text)
#     order = await state.get_data()
#     await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
#     await bot.delete_message(chat_id=message.from_user.id, message_id=order["last_msg_id"])
    
    
#     msg = await message.answer(text="Выберите способ оплаты", reply_markup=order_kb())
#     await state.update_data(last_msg_id=msg.message_id)
    

# @cart_router.callback_query(F.data.startswith("money_"))
# async def nal(call: CallbackQuery, session_with_commit: AsyncSession, state: FSMContext):
#     _, money_flag = call.data.split('_')
#     purchase = await PurchaseDao.find_one_or_none(
#         session=session_with_commit,
#         filters=PurchaseModel(user_id=call.from_user.id,
#                               status="NEW")
#     )
#     order = await state.get_data()
#     await PurchaseDao.set_order(session_with_commit, data_id=purchase.id, getdate=order["date"], adress=order["adress"], status="WAIT", money=money_flag)
#     await state.clear()

#     if purchase.total < 500 : total=purchase.total+50
#     if money_flag == "1":
#         await call.answer(f"Оплата переводом.\n Итого: {total}₽\nРЕКВИЗИТЫ\nСпасибо за заказ\nКурьер напишет вам за 15 мин", show_alert=True)
#         money_text = f"Оплата переводом.\n"
#     else:
#         await call.answer(f"Оплата наличными. \n Итого: {total}₽\nСпасибо за заказ\nКурьер напишет вам за 15 мин", show_alert=True)
#         money_text = f"Оплата наличными.\n"
    
#     await page_home(call)
#     product_text=""
#     purchases = purchase.goods_id.split(', ')
#     for good in purchases:
#         if good.find('_') != -1:
#             product_id, taste_id = good.split('_')
#             taste = await TasteDao.find_one_or_none_by_id(session=session_with_commit, data_id=taste_id)
#             product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=product_id)
#             product_text += (f"🔹 {product.name} ({taste.taste_name})\n")
#         else: 
#             product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=good)
#             product_text += (f"🔹 {product.name}\n")
        
#     username = call.from_user.username
#     user_info = f"@{username}" if username else f"c ID {call.from_user.id}"
#     for admin_id in settings.ADMIN_IDS:
#         try:
            
#             await bot.send_message(
#                 chat_id=admin_id,
#                 text=(
#                     f"💲 Пользователь {user_info} оформил заказ\n"
#                     f"-------------------------------------------\n"
#                     f"{product_text}"
#                     f"за <b>{purchase.total} ₽</b> {money_text}"
#                     f"дата: {purchase.date}\n"
#                     f"адресс: {purchase.adress}\n"
#                 ), reply_markup=admin_accept_kb(user_id=call.from_user.id)
#             )
#         except Exception as e:
#             logger.error(f"Ошибка при отправке уведомления администраторам: {e}")