from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from dao.dao import PurchaseDao, UserDAO, ProductDao, TasteDao
from user.kbs import cart_kb, main_user_kb, purchases_kb
from user.schemas import PurchaseModel, PurchaseUserIDModel, TelegramIDModel, UserModel

user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    user_id = message.from_user.id
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=user_id)
    )
    if user_info:
        return await message.answer(
            f"👋 Привет, {message.from_user.full_name}! Выберите необходимое действие",
            reply_markup=main_user_kb(user_id)
        )

    values = UserModel(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await UserDAO.add(session=session_with_commit, values=values)
    await message.answer(f"🎉 <b>Благодарим за регистрацию!</b>. Теперь выберите необходимое действие.",
                         reply_markup=main_user_kb(user_id))

@user_router.callback_query(F.data == "home")
async def page_home(call: CallbackQuery):
    await call.answer("Главная страница")
    return await call.message.edit_text(
        f"👋 Привет, {call.from_user.full_name}! Выберите необходимое действие",
        reply_markup=main_user_kb(call.from_user.id)
    )

@user_router.callback_query(F.data == "about")
async def page_about(call: CallbackQuery):
    await call.answer("Информация")
    await call.message.edit_text(
        text=(
            "🎓 Добро пожаловать в систему заказов!\n\n"
            "Только безналичная оплата. В случае отмены заказа предоплата не возвращается.\n\n"
            "Доставка осуществляется только по г. Звенигород.\n"
            "Сумма доставки 50₽. При сумме заказа от 500₽ доставка бесплано.\n\n"
            "Заказ можно проверить на месте при курьере.\n\n"
            "Предупредим за 15 минут до доставки.\n\n"
        ),
        reply_markup=call.message.reply_markup
    )

@user_router.callback_query(F.data == "my_profile")
async def page_profil(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Профиль")

    # Получаем статистику покупок пользователя
    statistic = await UserDAO.get_purchase_statistics(
        session=session_without_commit,
        telegram_id=call.from_user.id
    )
    
    total_amount = statistic.get("total_amount", 0)
    total_purchases = statistic.get("total_purchases", 0)
    # Формируем сообщение в зависимости от наличия покупок
    text=''
    if total_purchases == 0:
        await call.message.edit_text(
            text="🔍 <b>У вас пока нет покупок.</b>\n\n"
                 "Откройте каталог и выберите что-нибудь интересное!",
            reply_markup=main_user_kb(call.from_user.id)
        )
    else:
        text = (
            f"🛍 <b>Ваш профиль:</b>\n\n"
            f"Количество заказов: <b>{total_purchases}</b>\n"
            f"Итого: <b>{total_amount}₽</b>\n\n"
            # "Хотите просмотреть детали ваших покупок?"
        )
        await call.message.edit_text(
            text=text,
            reply_markup=purchases_kb()
        )
    purchases= await PurchaseDao.get_purchases(session=session_without_commit, telegram_id=call.from_user.id)
    if purchases is not None:
        logger.error(purchases)
        # for purchase in purchases:
        #     if (purchase.status=="NEW")


# @user_router.callback_query(F.data == "purchases")
# async def page_user_purchases(call: CallbackQuery, session_without_commit: AsyncSession):
#     await call.answer("Мои покупки")

#     # Получаем список покупок пользователя
#     purchases = await PurchaseDao.get_purchases(session=session_without_commit, telegram_id=call.from_user.id)
#     if not purchases:
#         await call.message.edit_text(
#             text=f"🔍 <b>У вас пока нет покупок.</b>\n\n"
#                  f"Откройте каталог и выберите что-нибудь интересное!",
#             reply_markup=main_user_kb(call.from_user.id)
#         )
#         return
#     product_text = (
#             f"🛒 <b>Информация о ваших покупках:</b>\n"
#             f"━━━━━━━━━━━━━━━━━━\n")
#     # Для каждой покупки отправляем информацию
#     for purchase in purchases:
#         products = purchase.goods_id.split(', ')
#         for good in products:
#             if good.find('_') != -1:
#                 product_id, taste_id = good.split('_')
#                 taste = await TasteDao.find_one_or_none_by_id(session=session_without_commit, data_id=taste_id)
#                 product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=product_id)
#                 product_text += (f"🔹 {product.name} ({taste.taste_name})\n")
#             else: 
#                 product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=good)
#                 product_text += (f"🔹 {product.name}\n")
#         if(purchase.status == "WAIT"): text_status = "Ожидает подтверждения"
#         elif(purchase.status == "CONFIRM"): text_status = "Ожидает доставки"
#         elif(purchase.status == "DONE"): text_status = "Выполнен"

#         product_text += (
#                 f"\n<b>итого:</b> {purchase.total}₽\n"
#                 f"<b>дата:</b> {purchase.date}\n"
#                 f"<b>адресс:</b> {purchase.adress}\n"
#                 f"<b>статус:</b> {text_status}\n"
#                 f"━━━━━━━━━━━━━━━━━━\n")

#     await call.message.edit_text(
#         text=product_text,
#         reply_markup=main_user_kb(call.from_user.id)
#     )

@user_router.callback_query(F.data == "cart")
async def page_user_cart(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Моя корзина")

    user_id = call.from_user.id
    purchase = await PurchaseDao.find_one_or_none(
        session=session_without_commit,
        filters=PurchaseModel(user_id=user_id,
                              status="NEW")
    )

    if not purchase:
        await call.message.edit_text(
            text=f"🔍 <b>У вас пока нет покупок.</b>\n\n"
                 f"Откройте каталог и выберите что-нибудь интересное!",
            reply_markup=main_user_kb(call.from_user.id)
        )
        return
    
    purchases = purchase.goods_id.split(', ')
    product_text = (
            f"🛒 <b>Информация о вашей корзине:</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n")
    
    # Для каждой покупки отправляем информацию
    for good in purchases:
        if good.find('_') != -1:
            product_id, taste_id = good.split('_')
            taste = await TasteDao.find_one_or_none_by_id(session=session_without_commit, data_id=taste_id)
            product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=product_id)
            product_text += (f"🔹 {product.name} ({taste.taste_name}) - {product.price} ₽\n")
        else: 
            product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=good)
            product_text += (f"🔹 {product.name} - {product.price} ₽\n")

    product_text += (f"━━━━━━━━━━━━━━━━━━\n")
    if purchase.total < 500 : 
        product_text += (f"Итого: {purchase.total+50}₽ с учетом доставки\n")
    else:
        product_text += (f"Итого: {purchase.total}₽. Доставка бесплатно.\n")

    await call.message.edit_text(
        text=product_text,
        reply_markup=cart_kb()
    )