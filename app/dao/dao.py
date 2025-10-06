from datetime import datetime, timedelta, date
import json
from typing import Optional, List, Dict

from loguru import logger
from sqlalchemy import select, func, case
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dao.base import BaseDAO
from dao.models import Taste, User, Purchase, Category, Product

class CategoryDao(BaseDAO[Category]):
    model = Category

    @classmethod
    async def save_all(cls, session: AsyncSession) -> Optional[List[Product]]:
        try:
            results = session.query(Category).all()
            json_data = [u._asdict() for u in results]
            json_output = json.dumps(json_data)
            print(json_output)
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при выгрузке в файл: {e}")
            return None

class ProductDao(BaseDAO[Product]):
    model = Product

    @classmethod
    async def get_products(cls, session: AsyncSession, category_id: int) -> Optional[List[Product]]:
        try:
            # Запрос для получения продуктов
            result = await session.execute(
                select(Product)
                .filter(Product.category_id == category_id, Product.quantity > 0)
                ) 
            products = result.scalars().all() 
            if products is None:
                return None 
            return products
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении корзины: {e}")
            return None
        

    @classmethod
    async def edit_quantity_product(cls, session: AsyncSession, product_id: int, do_less: bool):
        try:
            # Запрос для уменьшения кол-во продукта
            product = session.get(Product, product_id)
            logger.error(product)
            if product:
                if do_less:
                    product.quantity -= 1
                else:
                    product.quantity += 1
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении корзины: {e}")
            return None
        

        
class TasteDao(BaseDAO[Taste]):
    model = Taste
    
    @classmethod
    async def get_tastes(cls, session: AsyncSession, product_id: int) -> Optional[List[Taste]]:
        try:
            # Запрос для получения продуктов
            result = await session.execute(
                select(Taste)
                .filter(Taste.product_id == product_id, Taste.quantity > 0)
                )
            tastes = result.scalars().all() 
            # logger.error(user)
            if tastes is None:
                return None 
            return tastes
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении корзины: {e}")
            return None

    @classmethod
    async def edit_quantity_taste(cls, session: AsyncSession, taste_id: int, do_less: bool):
        try:
            # Запрос для уменьшения кол-во продукта
            taste = session.get(Taste, taste_id)
            if taste:
                if do_less:
                    taste.quantity -= 1
                else:
                    taste.quantity += 1
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении корзины: {e}")
            return None

class PurchaseDao(BaseDAO[Purchase]):
    model = Purchase

    @classmethod
    async def set_order(cls, session: AsyncSession, data_id: int, getdate: int, adress: str):
        try:
            record = await session.get(cls.model, data_id)
            setDate=datetime.strptime(getdate, "%d/%m/%Y").date()
            setattr(record, 'date', setDate)
            setattr(record, 'adress', adress)
            await session.flush()
        except SQLAlchemyError as e:
            print(e)
            raise e
        
    @classmethod
    async def get_purchases(cls, session: AsyncSession, telegram_id: int, isFlag:str) -> Optional[List[Purchase]]:
        try:
            # Запрос для получения пользователя с его покупками и связанными продуктами
            result = await session.execute(
                select(Purchase)
                .options(selectinload(Purchase.product))
                .options(selectinload(Purchase.taste))
                .filter(Purchase.user_id == telegram_id, Purchase.status == isFlag)
                )
            purchases = result.scalars().all() 
            if purchases is None:
                return None 
            return purchases 
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении информации о покупках пользователя: {e}")
            return None
        
    @classmethod
    async def get_total(cls, session: AsyncSession, telegram_id: int, isFlag: str) -> Optional[List[Purchase]]:
        try:
            # Запрос для получения суммы корзины
            result = await session.execute(
                select(func.sum(Product.price).label('total_price'))
                .join(Purchase).filter(Purchase.user_id == telegram_id, Purchase.status == isFlag)
                )
            total_price = result.scalars().one_or_none()
            return total_price if total_price is not None else 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении суммы заказа: {e}")
            raise

    @classmethod
    async def get_delivery(cls, session: AsyncSession) -> Optional[List[Purchase]]:
        try:
            # Запрос для получения доставок сегодня
            result = await session.execute(
                select(Purchase)
                .filter(Purchase.status == "NEW")
                .order_by(Purchase.user_id)
                )
            total_price = result.scalars().all()
            return total_price if total_price is not None else 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении суммы заказа: {e}")
            raise

    @classmethod
    async def get_user_today(cls, session: AsyncSession) -> Optional[List[Purchase]]:
        try:
            # Запрос для получения доставок сегодня
            result = await session.execute(
                select(User)
                .join(Purchase)
                .filter(Purchase.status == "CONFIRM")
                .order_by(Purchase.user_id)
                .group_by(Purchase.user_id)
                )
            total_price = result.scalars().all()
            return total_price if total_price is not None else 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении суммы заказа: {e}")
            raise
        
    @classmethod
    async def get_full_summ(cls, session: AsyncSession) -> int:
        """Получить общую сумму покупок."""
        query = select(func.sum(cls.model.price).label('total_price'))
        result = await session.execute(query)
        total_price = result.scalars().one_or_none()
        return total_price if total_price is not None else 0
    
    @classmethod
    async def change_status (cls, session: AsyncSession, purchase_id: int, status:str):
        try:
            # Запрос для уменьшения кол-во продукта
            purchase = await session.get(Purchase, purchase_id)
            if purchase:
                setattr(purchase, 'status', status)
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении корзины: {e}")
            return None

class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def get_purchase_statistics(cls, session: AsyncSession, telegram_id: int) -> Optional[Dict[str, int]]:
        try:
            # Запрос для получения общего числа покупок и общей суммы
            result = await session.execute(
                select(
                    func.count(Purchase.id).label('total_purchases'),
                    func.sum(Product.price).label('total_amount')
                )
                .join(User).filter(User.telegram_id == telegram_id)
                .join(Product).filter(Product.id == Purchase.product_id)
            )
            stats = result.one_or_none()

            if stats is None:
                return None

            total_purchases, total_amount = stats
            return {
                'total_purchases': total_purchases,
                'total_amount': total_amount or 0  # Обработка случая, когда сумма может быть None
            }

        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении статистики покупок пользователя: {e}")
            return None
        

        
    @classmethod
    async def get_purchased_products(cls, session: AsyncSession, telegram_id: int) -> Optional[List[Purchase]]:
        try:
            # Запрос для получения пользователя с его покупками и связанными продуктами
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.purchases).selectinload(Purchase.product)
                )
                .filter(User.telegram_id == telegram_id)
                )
            user = result.scalar_one_or_none()
            if user is None:
                return None 
            return user.purchases 
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении информации о покупках пользователя: {e}")
            return None

                
    @classmethod
    async def get_statistics(cls, session: AsyncSession):
        try:
            now = datetime.now()
            query = select(
                func.count().label('total_users'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=1), 1), else_=0)).label('new_today'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=7), 1), else_=0)).label('new_week'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=30), 1), else_=0)).label('new_month')
            )
            result = await session.execute(query)
            stats = result.fetchone()
            statistics = {
                'total_users': stats.total_users,
                'new_today': stats.new_today,
                'new_week': stats.new_week,
                'new_month': stats.new_month
            }
            logger.info(f"Статистика успешно получена: {statistics}")
            return statistics
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            raise