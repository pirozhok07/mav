from typing import List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dao.models import Category
from datetime import date, timedelta

def catalog_admin_kb(catalog_data: List[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=category.category_name, callback_data=f"add_category_{category.id}")
    kb.button(text="❌ Отмена", callback_data="admin_panel")
    kb.adjust(2)
    return kb.as_markup()


def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data="statistic")
    kb.button(text="🛍️ Управлять товарами", callback_data="process_products")
    kb.button(text="✅ Доставки", callback_data="delivery")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
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
    kb.button(text="🗑️ Удалить товар", callback_data="delete_product")
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2, 2, 1)
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

def admin_delivery_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✔ Доставлен", callback_data=f"deliver_order_{user_id}")
    kb.button(text="Перенести", callback_data=f"deliver_transferred_{user_id}")
    kb.adjust(1)
    return kb.as_markup()