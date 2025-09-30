from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from dao.dao import PurchaseDao, UserDAO, ProductDao, TasteDao
from user.kbs import cart_kb, main_user_kb, purchases_kb
from user.schemas import TasteIDModel, TelegramIDModel, UserModel, CartModel

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
    await call.answer("О магазине")
    await call.message.edit_text(
        text=(
            "🎓 Добро пожаловать в магазин!\n\n"
        ),
        reply_markup=call.message.reply_markup
    )

@user_router.callback_query(F.data == "my_profile")
async def page_about(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Профиль")

    # Получаем статистику покупок пользователя
    purchases = await UserDAO.get_purchase_statistics(session=session_without_commit, telegram_id=call.from_user.id)
    total_amount = purchases.get("total_amount", 0)
    total_purchases = purchases.get("total_purchases", 0)

    # Формируем сообщение в зависимости от наличия покупок
    if total_purchases == 0:
        await call.message.edit_text(
            text="🔍 <b>У вас пока нет покупок.</b>\n\n"
                 "Откройте каталог и выберите что-нибудь интересное!",
            reply_markup=main_user_kb(call.from_user.id)
        )
    else:
        text = (
            f"🛍 <b>Ваш профиль:</b>\n\n"
            f"Количество купленных товаров: <b>{total_purchases}</b>\n"
            f"Общая сумма: <b>{total_amount}₽</b>\n\n"
            "Хотите просмотреть детали ваших покупок?"
        )
        await call.message.edit_text(
            text=text,
            reply_markup=purchases_kb()
        )

@user_router.callback_query(F.data == "purchases")
async def page_user_purchases(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Мои покупки")

    # Получаем список покупок пользователя
    purchases = await UserDAO.get_purchased_products(session=session_without_commit, telegram_id=call.from_user.id)
    if not purchases:
        await call.message.edit_text(
            text=f"🔍 <b>У вас пока нет покупок.</b>\n\n"
                 f"Откройте каталог и выберите что-нибудь интересное!",
            reply_markup=main_user_kb(call.from_user.id)
        )
        return
    product_text = (
            f"🛒 <b>Информация о ваших покупках:</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n")
    # Для каждой покупки отправляем информацию
    for purchase in purchases:
        product = purchase.product
        if purchase.taste_id != 0:
            taste = await TasteDao.find_one_or_none(
                session=session_without_commit,
                filters=TasteIDModel(id=purchase.taste_id)
            )
            product_text += (f"🔹 {product.name} ({taste.taste_name}) - {product.price} ₽\n")
        else:
             product_text += (f"🔹 {product.name} - {product.price} ₽\n")

    await call.message.edit_text(
        text=product_text,
        reply_markup=main_user_kb(call.from_user.id)
    )

@user_router.callback_query(F.data == "cart")
async def page_user_cart(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Моя корзина")

    # Получаем список покупок пользователя
    # cart = await ProductDao.find_all(session=session_without_commit,
                                                #   filters=CartModel(id=call.from_user.id))
    # count_products = len(products_category)
    purchases = await PurchaseDao.get_purchases(session=session_without_commit, telegram_id=call.from_user.id)
    # logger.error(purchases)
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

        # logger.error(purchase)
        product = purchase.product
        # logger.error(product)
        # file_text = "📦 <b>Товар включает файл:</b>" if product.file_id else "📄 <b>Товар не включает файлы:</b>"
        if purchase.taste_id != 0:
            taste = await TasteDao.find_one_or_none(
                session=session_without_commit,
                filters=TasteIDModel(id=purchase.taste_id)
            )
            product_text += (f"🔹 {product.name} ({taste.taste_name}) - {product.price} ₽\n")
        else:
             product_text += (f"🔹 {product.name} - {product.price} ₽\n")
        cart_total +=product.price
    product_text += (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"сумма заказа: {cart_total}₽\n")

    await call.message.edit_text(
        text=product_text,
        reply_markup=cart_kb()
    )