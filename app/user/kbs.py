from typing import List
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from loguru import logger
from dao.dao import TasteDao
from user.schemas import TasteIDModel
from config import settings
from dao.models import Category, Product, Purchase, Taste
from datetime import datetime

def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Каталог", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="👤 Мои покупки", callback_data="my_profile")
    kb.button(text="ℹ️ О магазине", callback_data="about")
    # kb.button(text="🌟 Поддержать автора 🌟", url='https://t.me/tribute/app?startapp=deLN')
    if user_id in settings.ADMIN_IDS:
        kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def catalog_kb(catalog_data: List[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=category.category_name, callback_data=f"category_{category.id}")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()



def purchases_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📜 Смотреть покупки", callback_data="purchases")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


# def product_kb_1(product_id) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Показать вкусы", callback_data=f"show_taste_{product_id}")
#     kb.adjust(1)
#     return kb.as_markup()

def product_kb(product_data: List[Product]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for product in product_data:
        if product.category_id == 3:
            kb.button(text=f"{product.name} - {product.price} ₽", callback_data=f"taste_{product.id}")
        else:
            kb.button(text=f"{product.name} - {product.price} ₽", callback_data=f"cart_{product.id}_0")
    kb.button(text="🛍 Назад", callback_data="catalog")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

# def taste_kb(taste_data: List[Taste]) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     for taste in taste_data:
#         kb.button(text=taste.taste_name, callback_data=f"taste_{taste.id}")
#     kb.button(text="🛍 Назад", callback_data="category_1")
#     kb.button(text="🏠 На главную", callback_data="home")
#     kb.adjust(2)
#     return kb.as_markup()
# def product_kb(product_id) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="💸 В корзину", callback_data=f"cart_{product_id}")
#     kb.adjust(1)
#     return kb.as_markup()

def taste_kb(taste_data: List[Taste]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for taste in taste_data:
        kb.button(text=taste.taste_name, callback_data=f"cart_{taste.product_id}_{taste.id}")
    kb.button(text="🛍 Назад", callback_data="category_1")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def delete_kb(purchase_data: List[Purchase]) -> InlineKeyboardMarkup:
    logger.error(purchase_data)
    kb = InlineKeyboardBuilder()
    for purchase in purchase_data:
        product = purchase.product
        if purchase.taste_id != 0:
            taste = purchase.taste
            kb.button(text=f"{product.name} ({taste.taste_name}) - {product.price}₽", callback_data=f"itemDell_{purchase.id}_{purchase.product_id}_{purchase.taste_id}")
        else:
            kb.button(text=f"{product.name} - {product.price}₽", callback_data=f"itemDell_{purchase.id}_{purchase.product_id}_0")
    kb.button(text="🛍 Назад", callback_data="cart")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def cart_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Оформить заказ", callback_data=f"do_order")
    kb.button(text="✖ Редактировать корзину", callback_data=f"edit_cart")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def date_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    f = datetime.now()
    kb.button(text=f, callback_data=f"item_dell_")
    kb.adjust(1)
    return kb.as_markup()


def cancele_kb()-> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Назад", callback_data="cart")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()

def order_kb()-> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Наличные", callback_data="nal")
    kb.button(text="💳 Перевод", callback_data="nenal")
    kb.adjust(2)
    return kb.as_markup()

def get_product_buy_kb(price) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'💲 Оплатить {price}₽', pay=True)],
        [InlineKeyboardButton(text='⛔ Отменить', callback_data='home')]
    ])

