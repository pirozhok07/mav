from datetime import datetime, date
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, Integer, DATE
from dao.database import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    purchases: Mapped[List['Purchase']] = relationship("Purchase", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"


class Category(Base):
    __tablename__ = 'categories'

    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.category_name}')>"


class Product(Base):
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int]
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    tastes: Mapped[List['Taste'] | None] = relationship("Taste", back_populates="product")
    purchases: Mapped[List['Purchase']] = relationship("Purchase", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', category_id='{self.category_id}', quantity='{self.quantity}', price={self.price})>"
    
class Taste(Base):
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    taste_name: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    product: Mapped["Product"] = relationship("Product", back_populates="tastes")
    purchases: Mapped[List['Purchase']] = relationship("Purchase", back_populates="taste")

    def __repr__(self):
        return f"<Taste(id={self.id}, taste_name='{self.taste_name}', quantity={self.quantity})>"


class Purchase(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    taste_id: Mapped[int] = mapped_column(ForeignKey('tastes.id'), nullable=True)
    status: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    adress: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(DATE, nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="purchases")
    product: Mapped["Product"] = relationship("Product", back_populates="purchases")
    taste: Mapped["Taste"] = relationship("Taste", back_populates="purchases")

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, taste_id={self.taste_id}, date={self.date}, satus={self.status})>"