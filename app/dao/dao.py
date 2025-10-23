from datetime import datetime, time, timedelta, date
import json
from typing import Optional, List, Dict

from loguru import logger
from sqlalchemy import select, func, case
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dao.base import BaseDAO
from dao.models import Taste, User, Purchase, Category, Product, Delivery, DeliveryTime

class DeliveryTimeDao(BaseDAO[DeliveryTime]):
    model = DeliveryTime

    @classmethod
    async def set_new_time(cls, session: AsyncSession, get_date:date, set_time:time):
        try:
            result = await session.execute(
                select(DeliveryTime.id)
                .filter(DeliveryTime.date == get_date)
                )
            o = result.one_or_none()
            logger.error(o)
            record = await session.get(cls.model, o)

            setattr(record, 'time', set_time)
            logger.error(record)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении суммы заказа: {e}")
            raise

class DeliveryDao(BaseDAO[Delivery]):
    model = Delivery

    @classmethod
    async def get_delivery_adress(cls, session: AsyncSession) -> Optional[List[str]]:
        try:
            # Запрос для получения доставок сегодня
            result = await session.execute(
                select(Delivery.adress)
                )
            adress = result.scalars().all()
            if adress is None:
                return None 
            return adress
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении суммы заказа: {e}")
            raise
    
    @classmethod
    async def get_delivery_date(cls, session: AsyncSession):
        try:
            # Запрос для получения доставок сегодня
            result = await session.execute(
                select(Delivery.date)
                .group_by(Delivery.date)
                )
            orderDate = result.scalars().all()
            if orderDate is None:
                return None
            return orderDate
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении суммы заказа: {e}")
            raise

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
    async def set_order(cls, session: AsyncSession, 
                        data_id: int, 
                        quantity: int = None,
                        price: int = None):
        try:
            record = await session.get(cls.model, data_id)
            if quantity is not None: setattr(record, 'quantity', quantity)
            if price is not None: setattr(record, 'price', price)
            await session.flush()
        except SQLAlchemyError as e:
            print(e)
            raise e

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
    async def set_order(cls, session: AsyncSession, 
                        data_id: int, 
                        quantity: int):
        try:
            record = await session.get(cls.model, data_id)
            if quantity is not None: setattr(record, 'quantity', quantity)
            await session.flush()
        except SQLAlchemyError as e:
            print(e)
            raise e
        
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
    async def delete_old(cls, session: AsyncSession, status:str):
        # Удалить записи по фильтру
        try:
            # Запрос для получения пользователя с его покупками и связанными продуктами
            result = await session.execute(
            select(Purchase)
            .filter(Purchase.status == status)
            )
            
            purchases = result.scalars().all() 
            for item in purchases:
                await session.delete(item)
            logger.error("DONE")
            return None 
        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при удалении объекта: {e}")
            return None
        
    @classmethod
    async def set_order(cls, session: AsyncSession, 
                        data_id: int, 
                        getdate: int = None, 
                        adress: str= None, 
                        money:bool=None,
                        goods:str = None,
                        total:int=None,
                        status:str=None):
        try:
            record = await session.get(cls.model, data_id)
            if adress is not None: setattr(record, 'adress', adress)
            if goods is not None: setattr(record, 'goods_id', goods)
            if total is not None: setattr(record, 'total', total)
            if status is not None: setattr(record, 'status', status)
            if getdate is not None: 
                setDate=datetime.strptime(getdate, "%d.%m.%Y").date()
                setattr(record, 'date', setDate)
            
            if money is not None: 
                if money == "1":
                    setattr(record, 'money', True)
                else:
                    setattr(record, 'money', False)
            await session.flush()
        except SQLAlchemyError as e:
            print(e)
            raise e
        
    @classmethod
    async def get_purchases(cls, session: AsyncSession, telegram_id: int) -> Optional[List[Purchase]]:
        try:
            # Запрос для получения пользователя с его покупками и связанными продуктами
            result = await session.execute(
            select(Purchase)
            .filter(Purchase.user_id == telegram_id, Purchase.status =="NEW" or Purchase.status =="COMFIRM")
            .order_by(Purchase.date)
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
    async def get_total(cls, session: AsyncSession, telegram_id: int, isFlag: str, get_date:date = None) -> Optional[List[Purchase]]:
        try:
            # Запрос для получения суммы корзины
            result = await session.execute(
                select(func.sum(Product.price).label('total_price'))
                .join(Purchase).filter(Purchase.user_id == telegram_id, Purchase.status == isFlag, Purchase.date == get_date)
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
    async def get_delivery_adress(cls, session: AsyncSession, getdate:date) -> Optional[List[str]]:
        try:
            # Запрос для получения доставок сегодня
            result = await session.execute(
                select(Purchase.adress)
                .filter(Purchase.status == "CONFIRM", Purchase.date == getdate)
                .group_by(Purchase.adress)
                )
            total_price = result.scalars().all()
            logger.error(total_price)
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
                    func.sum(Purchase.total).label('total_amount')
                )
                .join(User).filter(User.telegram_id == telegram_id)
                .filter(Purchase.status != "NEW")
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