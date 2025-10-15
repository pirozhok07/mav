from typing import List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from dao.models import Category, Product, Taste
from datetime import date, timedelta

def catalog_admin_kb(catalog_data: List[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=category.category_name, callback_data=f"add_category_{category.id}")
    kb.button(text="❌ Отмена", callback_data="admin_panel")
    kb.adjust(2)
    return kb.as_markup()

def admin_catalog_kb(catalog_data: List[Category], isFlag:str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=category.category_name, callback_data=f"adminCategory_{isFlag}_{category.id}")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def admin_product_kb(product_data: List[Product], isFlag:str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for product in product_data:
        if isFlag =="0": data=f"{product.quantity} шт"
        else: data=f"{product.price} ₽"
        if product.category_id == 3 and isFlag =="0":
            kb.button(text=f"{product.name} - {data}", callback_data=f"adminTaste_{product.id}")
        else:
            kb.button(text=f"{product.name} - {data}", callback_data=f"adminGood_{isFlag}_{product.id}_0")
    kb.button(text="🛍 Назад", callback_data="edit_product")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def admin_taste_kb(taste_data: List[Taste]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for taste in taste_data:
        kb.button(text=f"{taste.taste_name} - {taste.quantity} шт", callback_data=f"adminGood_0_{taste.product_id}_{taste.id}")
    kb.button(text="🛍 Назад", callback_data=f"adminCategory_0_{taste_data[0].product_id}")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data="statistic")
    kb.button(text="🛍️ Управлять товарами", callback_data="process_products")
    kb.button(text="✅ Доставки", callback_data="delivery")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def admin_kb_back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def admin_date_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    f = date.today()
    for i in range(0,3):
        nextday=timedelta(i)
        btn = (f+nextday).strftime("%d.%m.%Y")
        kb.button(text=btn, callback_data=f"delivery_date_{btn}")
    kb.button(text="Отмена", callback_data="cancel")
    kb.adjust(1)
    return kb.as_markup()

def admin_adress_kb(adress_data:List[str]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i in adress_data:
        logger.error(i)
        kb.button(text=i, callback_data=f"delivery_adress_{i}")
    kb.button(text="Отмена", callback_data="cancel")
    kb.adjust(1)
    return kb.as_markup()

def admin_show_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Показать", callback_data=f"delivery_show")
    kb.button(text="Отмена", callback_data="cancel")
    kb.adjust(1)
    return kb.as_markup()

def dell_product_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑️ Удалить", callback_data=f"dell_{product_id}")
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def product_management_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить товар", callback_data="add_product")
    kb.button(text="🗑️ Редактировать кол-во", callback_data="edit_product_0")
    kb.button(text="🗑️ Редактировать цену", callback_data="edit_product_1")
    kb.button(text="🗑️ Удалить товар", callback_data="delete_product")
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def cancel_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="cancel")
    return kb.as_markup()


def admin_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Все верно", callback_data="confirm_add")
    kb.button(text="Отмена", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def admin_accept_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✔ Подтвердить", callback_data=f"acceptOrder_{user_id}")
    kb.adjust(1)
    return kb.as_markup()

def admin_delivery_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✔ Доставлены", callback_data="deliver_order")
    kb.button(text="Перенести", callback_data="deliver_transferred")
    kb.adjust(1)
    return kb.as_markup()
