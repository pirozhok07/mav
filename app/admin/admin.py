import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from loguru import logger
from user.schemas import PurchaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings, bot
from dao.dao import DeliveryDao, TasteDao, UserDAO, ProductDao, CategoryDao, PurchaseDao
from admin.kbs import admin_adress_kb, admin_catalog_kb, admin_date_kb, admin_delivery_kb, admin_kb, admin_kb_back, admin_product_kb, admin_taste_kb, product_management_kb, cancel_kb_inline, catalog_admin_kb, \
    admin_confirm_kb, dell_product_kb
from admin.schemas import DeliveryData, ProductModel, ProductIDModel, PurchaseDateModel, UserIDModel
from admin.utils import process_dell_text_msg
from datetime import date, datetime

admin_router = Router()

class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    category_id = State()
    hidden_content = State()
    confirm_add = State()

class ChangeProductQuantity(StatesGroup):
    value = State()
    isTaste = State()
    id_Taste = State()
    id_Product = State()
    isPrice = State()

class ChangeProductPrice(StatesGroup):
    price = State()

class DeliveryOrder(StatesGroup):
    adress = State()

@admin_router.callback_query(F.data == "cancel", F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_process_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отмена сценария добавления товара')
    await call.message.delete()
    await call.message.edit_text(
        text="Отмена добавления товара.",
        reply_markup=admin_kb_back()
    )

@admin_router.callback_query(F.data == "all_p", F.from_user.id.in_(settings.ADMIN_IDS))
async def all_p(call: CallbackQuery, session_without_commit: AsyncSession):
    purchases = await DeliveryDao.find_all(session=session_without_commit)
    for purchase in purchases:
        logger.error(purchase)

@admin_router.callback_query(F.data == "admin_panel", F.from_user.id.in_(settings.ADMIN_IDS))
async def start_admin(call: CallbackQuery):
    await call.answer('Доступ в админ-панель разрешен!')
    await call.message.edit_text(
        text="Вам разрешен доступ в админ-панель. Выберите необходимое действие.",
        reply_markup=admin_kb()
    )

@admin_router.callback_query(F.data == 'statistic', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_statistic(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Запрос на получение статистики...')
    await call.answer('📊 Собираем статистику...')

    stats = await UserDAO.get_statistics(session=session_without_commit)
    total_summ = await PurchaseDao.get_full_summ(session=session_without_commit)
    stats_message = (
        "📈 Статистика пользователей:\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🆕 Новых за сегодня: {stats['new_today']}\n"
        f"📅 Новых за неделю: {stats['new_week']}\n"
        f"📆 Новых за месяц: {stats['new_month']}\n\n"
        f"💰 Общая сумма заказов: {total_summ} руб.\n\n"
        "🕒 Данные актуальны на текущий момент."
    )
    await call.message.edit_text(
        text=stats_message,
        reply_markup=admin_kb()
    )

@admin_router.callback_query(F.data == 'process_products', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_process_products(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим управления товарами')
    all_products_count = await ProductDao.count(session=session_without_commit)
    await call.message.edit_text(
        text=f"На данный момент в базе данных {all_products_count} товаров. Что будем делать?",
        reply_markup=product_management_kb()
    )

@admin_router.callback_query(F.data == 'delete_product', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим удаления товаров')
    all_products = await ProductDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text=f"На данный момент в базе данных {len(all_products)} товаров. Для удаления нажмите на кнопку ниже"
    )
    for product_data in all_products:
        file_id = product_data.file_id
        file_text = "📦 Товар с файлом" if file_id else "📄 Товар без файла"

        product_text = (f'🛒 Описание товара:\n\n'
                        f'🔹 <b>Название товара:</b> <b>{product_data.name}</b>\n'
                        f'🔹 <b>Описание:</b>\n\n<b>{product_data.description}</b>\n\n'
                        f'🔹 <b>Цена:</b> <b>{product_data.price} ₽</b>\n'
                        f'🔹 <b>Описание (закрытое):</b>\n\n<b>{product_data.hidden_content}</b>\n\n'
                        f'<b>{file_text}</b>')
        if file_id:
            await call.message.answer_document(document=file_id, caption=product_text,
                                               reply_markup=dell_product_kb(product_data.id))
        else:
            await call.message.answer(text=product_text, reply_markup=dell_product_kb(product_data.id))

@admin_router.callback_query(F.data.startswith('dell_'), F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(call.data.split('_')[-1])
    await ProductDao.delete(session=session_with_commit, filters=ProductIDModel(id=product_id))
    await call.message.edit_text(f"Товар с ID {product_id} удален!", show_alert=True)
    await call.message.delete()

@admin_router.callback_query(F.data.startswith("add_category_"),
                             F.from_user.id.in_(settings.ADMIN_IDS),
                             AddProduct.category_id)
async def admin_process_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split("_")[-1])
    await state.update_data(category_id=category_id)
    await call.answer('Категория товара успешно выбрана.')
    msg = await call.message.edit_text(text="Введите цену товара: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.price)

@admin_router.callback_query(F.data.startswith("edit_product_"),
                             F.from_user.id.in_(settings.ADMIN_IDS))
async def edit_product(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка каталога...")
    isFlag = call.data.split("_")[-1]
    catalog_data = await CategoryDao.find_all(session=session_without_commit)
    await call.message.edit_text(
        text="Выберите категорию товаров:",
        reply_markup=admin_catalog_kb(catalog_data, isFlag)
    )

@admin_router.callback_query(F.data.startswith("adminCategory_"),
                             F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_category_(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка товаров...")
    _, isFlag, category_id = call.data.split("_")
    product_data = await ProductDao.get_products(session=session_without_commit, category_id=category_id)
    count_products = len(product_data)
    if count_products:
        await call.message.edit_text(
            text=f"В данной категории {count_products} товаров.",
            reply_markup=admin_product_kb(product_data, isFlag)
        )
    else:
        catalog_data = await CategoryDao.find_all(session=session_without_commit)
        await call.message.edit_text(text="В данной категории нет товаров.\n\n Выберите категорию товаров:", reply_markup=admin_catalog_kb(catalog_data)) # возврат

@admin_router.callback_query(F.data.startswith("adminTaste_"),
                             F.from_user.id.in_(settings.ADMIN_IDS))
async def adminTaste(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка вкусов...")
    product_id = int(call.data.split("_")[-1])    
    taste_data = await TasteDao.get_tastes(session=session_without_commit, product_id=product_id)
    await call.message.edit_text(
        text="Выберите вкус:",
        reply_markup=admin_taste_kb(taste_data))


@admin_router.callback_query(F.data.startswith('adminGood_'))
async def adminGood(call: CallbackQuery | Message, session_with_commit: AsyncSession, state: FSMContext):
    await call.answer("Изменение кол-во")
    _, isFlag, product_id, taste_id = call.data.split('_')
    product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=int(product_id))
    if taste_id != "0":
        taste = await TasteDao.find_one_or_none_by_id(session=session_with_commit, data_id=int(taste_id))
        text_data=(f"В наличие <b>{taste.quantity}</b> шт.\n"
                   f"{product.name} ({taste.taste_name})"
        )
        await state.update_data(isTaste=True)
        await state.update_data(id_Taste=taste_id)
    else:
        if isFlag == "0":
            text_data=(f"В наличие <b>{product.quantity}</b> шт.\n"
                       f"{product.name}"
            )
        else:
            text_data=(f"Цена <b>{product.price}</b> ₽.\n"
                       f"{product.name}"
            )
        await state.update_data(isTaste=None)
    await state.update_data(id_Product=product_id)
    if isFlag == "0": await state.update_data(isPrice=None)
    else: await state.update_data(isPrice=True)
    msg = await call.message.edit_text(text=(f"{text_data}\n"
                                       f"Укажите количество товара: ")
    )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(ChangeProductQuantity.value)

@admin_router.message(F.text, F.from_user.id.in_(settings.ADMIN_IDS), ChangeProductQuantity.value)
async def admin_process_quantity(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.update_data(value=message.text)
    await process_dell_text_msg(message, state)
    data_order = await state.get_data()
    await state.clear()
    if data_order["isTaste"] is not None:
        product = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=data_order["id_Product"])
        taste = await TasteDao.find_one_or_none_by_id(session=session_with_commit, data_id=data_order["id_Taste"])
        setQuantity=product.quantity-taste.quantity
        await TasteDao.set_order(session_with_commit, data_id=data_order["id_Taste"], quantity=data_order["value"])
        await ProductDao.set_order(session_with_commit, data_id=data_order["id_Product"], quantity=setQuantity+int(data_order["value"]))
        await adminTaste(message,session_with_commit)
    else:
        if data_order["isPrice"] is not None:
            await ProductDao.set_order(session_with_commit, data_id=data_order["id_Product"], price=data_order["value"])
        else: 
            await ProductDao.set_order(session_with_commit, data_id=data_order["id_Product"], quantity=data_order["value"])

@admin_router.callback_query(F.data == 'add_product', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_process_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer('Запущен сценарий добавления товара.')
    msg = await call.message.edit_text(text="Для начала укажите имя товара: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.name)


@admin_router.message(F.text, F.from_user.id.in_(settings.ADMIN_IDS), AddProduct.name)
async def admin_process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await process_dell_text_msg(message, state)
    msg = await message.answer(text="Теперь дайте короткое описание товару: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.description)


@admin_router.message(F.text, F.from_user.id.in_(settings.ADMIN_IDS), AddProduct.description)
async def admin_process_description(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await state.update_data(description=message.html_text)
    await process_dell_text_msg(message, state)
    catalog_data = await CategoryDao.find_all(session=session_without_commit)
    msg = await message.answer(text="Теперь выберите категорию товара: ", reply_markup=catalog_admin_kb(catalog_data))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.category_id)

@admin_router.message(F.text, F.from_user.id.in_(settings.ADMIN_IDS), AddProduct.price)
async def admin_process_price(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    price = int(message.text)
    await state.update_data(price=price)
    await process_dell_text_msg(message, state)
    product_data = await state.get_data()
    category_info = await CategoryDao.find_one_or_none_by_id(session=session_without_commit,
                                                             data_id=product_data.get("category_id"))
    product_text = (f'🛒 Проверьте, все ли корректно:\n\n'
                    f'🔹 <b>Название товара:</b> <b>{product_data["name"]}</b>\n'
                    f'🔹 <b>Описание:</b>\n\n<b>{product_data["description"]}</b>\n\n'
                    f'🔹 <b>Цена:</b> <b>{product_data["price"]} ₽</b>\n'
                    f'🔹 <b>Категория:</b> <b>{category_info.category_name} (ID: {category_info.id})</b>\n\n')
    await process_dell_text_msg(message, state)
    msg = await message.answer(text=product_text, reply_markup=admin_confirm_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.confirm_add)


@admin_router.callback_query(F.data == "confirm_add", F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_process_confirm_add(call: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    await call.answer('Приступаю к сохранению файла!')
    product_data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=product_data["last_msg_id"])
    del product_data["last_msg_id"]
    await ProductDao.add(session=session_with_commit, values=ProductModel(**product_data))

@admin_router.callback_query(F.data.startswith("acceptOrder_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def accept_order(call: CallbackQuery, session_with_commit: AsyncSession):
    _, user_id = call.data.split("_")
    purchase = await PurchaseDao.find_one_or_none(
        session=session_with_commit,
        filters=PurchaseModel(user_id=user_id,
                              status="WAIT")
    )
    await PurchaseDao.change_status(session=session_with_commit, purchase_id=purchase.id, status = "CONFIRM")
    await call.message.edit_text(text=f"{call.message.text}\n <b>Подтвержден</b>.")

@admin_router.callback_query(F.data == 'delivery', F.from_user.id.in_(settings.ADMIN_IDS))
async def delivery_date(call: CallbackQuery):
    await call.answer("Доставки")
    await call.message.edit_text(text="Выберите дату доставки: ", reply_markup=admin_date_kb())

@admin_router.callback_query(F.data.startswith("delivery_date_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def delivery_adress(call: CallbackQuery, session_without_commit: AsyncSession, state: FSMContext):
    await call.answer("Доставки")
    date_text = call.data.split("_")[-1]
    date_order=datetime.strptime(date_text, "%d.%m.%Y").date()
    adresses = await PurchaseDao.get_delivery_adress(session=session_without_commit,
                                                     getdate=date_order)
    await state.update_data(adress=adresses)
    await call.message.edit_text(text="Выберите дату доставки: ", reply_markup=admin_adress_kb(adresses))  

@admin_router.callback_query(F.data.startswith("delivery_adress_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def delivery_adress(call: CallbackQuery, session_with_commit: AsyncSession, state: FSMContext):
    await call.answer("Доставки")
    adress_text = call.data.split("_")[-1]
    await DeliveryDao.add(session=session_with_commit, values=DeliveryData(adress=adress_text))
    data = await state.get_data()
    data["adress"].remove(adress_text)
    await state.update_data(adress=data["adress"])
    await call.message.edit_text(text="Выберите дату доставки: ", reply_markup=admin_adress_kb(data["adress"]))  

@admin_router.callback_query(F.data.startswith("delivery_date_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def show_delivery(call: CallbackQuery, session_without_commit: AsyncSession):
    date_text = call.data.split("_")[-1]
    date_order=datetime.strptime(date_text, "%d.%m.%Y").date()
    purchases = await PurchaseDao.find_all(session=session_without_commit,
                                           filters=PurchaseDateModel(date=date_order))
    logger.error(purchases)
    for purchase in purchases:
        products = purchase.goods_id.split(', ')
        product_text=""
        for good in products:
            if good.find('_') != -1:
                product_id, taste_id = good.split('_')
                taste = await TasteDao.find_one_or_none_by_id(session=session_without_commit, data_id=taste_id)
                product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=product_id)
                product_text += (f"🔹 {product.name} ({taste.taste_name})\n")
            else: 
                product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=good)
                product_text += (f"🔹 {product.name}\n")
        user= await UserDAO.find_one_or_none(session=session_without_commit,
                                      filters=UserIDModel(telegram_id=purchase.user_id))
        user_info = f"@{user.username}" if user.username else f"c ID {user.telegram_id}"
        if purchase.money: money_text = "наличными."
        else: money_text = "переводом."
        try:
            await bot.send_message(
                chat_id=call.from_user.id,
                text=(
                    f"💲 Пользователь {user_info}\n"
                    f"-------------------------------------------\n"
                    f"{product_text}"
                    f"за <b>{purchase.total} ₽</b> Оплата {money_text}\n"
                    f"адресс: {purchase.adress}\n"
                ), reply_markup=admin_delivery_kb(user.telegram_id)
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администраторам: {e}") 

@admin_router.callback_query(F.data.startswith("deliver_order_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def deliver_order(call: CallbackQuery, session_with_commit: AsyncSession):
    user_id = int(call.data.split("_")[-1])
    purchases = await PurchaseDao.get_purchases(session=session_with_commit, telegram_id=user_id)
    for purchase in purchases:
        await PurchaseDao.change_status(session=session_with_commit, purchase_id=purchase.id, status = "DONE")
    await call.message.answer(text="Заказ доставлен")

@admin_router.callback_query(F.data.startswith("deliver_transferred_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def deliver_transferred(call: CallbackQuery, session_with_commit: AsyncSession):
    user_id = int(call.data.split("_")[-1])
    purchases = await PurchaseDao.get_purchases(session=session_with_commit, telegram_id=user_id)
    for purchase in purchases:
        await PurchaseDao.change_status(session=session_with_commit, purchase_id=purchase.id, status = "DONE")
    await call.message.answer(text="Заказ доставлен")