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

# @catalog_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
@cart_router.callback_query(F.data.startswith('cart_'))
async def add_in_cart(call: CallbackQuery, session_with_commit: AsyncSession):
    await call.answer("Товар добавлен в корзину", show_alert=True)
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
        taste = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=product_id)
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
    await page_catalog(call, session_with_commit)



@cart_router.callback_query(F.data == 'edit_cart')
async def edit_cart(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим редактирования корзины')

    user_id = call.from_user.id
    purchase = await PurchaseDao.find_one_or_none(
        session=session_without_commit,
        filters=PurchaseModel(user_id=user_id,
                              status="NEW")
    )
    await call.message.edit_text(
        text="Выберите товар для удаления:",
        reply_markup=delete_kb(purchase.goods_id))

@cart_router.callback_query(F.data.startswith('itemDell_'))
async def dell_item(call: CallbackQuery, session_with_commit: AsyncSession):
    await call.answer("Товар удален из корзины", show_alert=True)
    _, purchase_id, product_id, taste_id = call.data.split('_')
    await call.answer(f"Заказ с ID {purchase_id} удален!")
    await ProductDao.update_one_by_id(session=session_with_commit, data_id=product_id, in_cart=False)
    if taste_id != "0":
        await TasteDao.update_one_by_id(session=session_with_commit, data_id=product_id, in_cart=False)
    await PurchaseDao.delete(session=session_with_commit, filters=PurchaseIDModel(id=purchase_id))
    await edit_cart(call, session_with_commit)

@cart_router.callback_query(F.data == 'do_order')
async def get_date(call: CallbackQuery, state: FSMContext):
    await call.answer("Оформление заказа")
    # await call.message.answer(f"Заказ будет доставлен ориентировочно сегодня после 19:30")
    msg = await call.message.edit_text(text="Для начала укажите дату доставки: ", reply_markup=date_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(DoOrder.date)

@cart_router.callback_query(F.data.startswith("get_date_"), DoOrder.date)
async def get_date(call: CallbackQuery, state: FSMContext):
    await call.answer("Оформление заказа")
    date = call.data.split("_")[-1]
    await state.update_data(date = date)
    # await call.message.answer(f"Заказ будет доставлен ориентировочно сегодня после 19:30")
    msg = await call.message.edit_text(text="Для начала укажите адресс доставки: ", reply_markup=cancele_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(DoOrder.adress)

@cart_router.message(F.text, DoOrder.adress)
async def get_adress(message: Message, state: FSMContext, session_with_commit: AsyncSession):
    await state.update_data(adress=message.text)
    order = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.from_user.id, message_id=order["last_msg_id"])
    purchases = await PurchaseDao.get_purchases(session=session_with_commit, telegram_id=message.from_user.id, isFlag="NEW")
    logger.error(purchases)
    for purchase in purchases:
        await PurchaseDao.set_order(session_with_commit, data_id=purchase.id, getdate=order["date"], adress=order["adress"])
        
    await state.clear()
    msg = await message.answer(text="Выберите способ оплаты", reply_markup=order_kb(order["date"]))
    await state.update_data(last_msg_id=msg.message_id)
    

@cart_router.callback_query(F.data.startswith("money_"))
async def nal(call: CallbackQuery, session_without_commit: AsyncSession):
    _, order_date, money_flag = call.data.split('_')
    total = await PurchaseDao.get_total(session=session_without_commit, telegram_id=call.from_user.id, isFlag="NEW", get_date=datetime.strptime(order_date, "%d.%m.%Y").date())
    purchases = await PurchaseDao.get_purchases(session=session_without_commit, telegram_id=call.from_user.id, isFlag="NEW", get_date=datetime.strptime(order_date, "%d.%m.%Y").date())
    if money_flag == "1":
        await call.answer(f"Оплата переводом.\nСумма к оплате: {total}₽\nРЕКВИЗИТЫ\nСпасибо за заказ\nКурьер напишет вам за 15 мин", show_alert=True)
        money_text = f"Оплата переводом.\n"
    else:
        await call.answer("Оплата наличными. \nСпасибо за заказ\nКурьер напишет вам за 15 мин", show_alert=True)
        money_text = f"Оплата наличными.\n"
    
    await page_home(call)
    text=''
    for purchase in purchases:
        await PurchaseDao.set_order(session_without_commit, data_id=purchase.id, money=money_flag)
        text += f"{purchase.product.name}\n"
    username = call.from_user.username
    user_info = f"@{username}" if username else f"c ID {call.from_user.id}"
    for admin_id in settings.ADMIN_IDS:
        try:
            
            await bot.send_message(
                chat_id=admin_id,
                text=(
                    f"💲 Пользователь {user_info} оформил заказ\n"
                    f"-------------------------------------------\n"
                    f"{text}"
                    f"за <b>{total} ₽</b> {money_text}"
                    f"дата: {order_date}\n"
                    f"адресс: {purchases[0].adress}\n"
                ), reply_markup=admin_accept_kb(user_id=call.from_user.id, date=order_date)
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администраторам: {e}")