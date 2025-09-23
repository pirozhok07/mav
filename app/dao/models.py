from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey
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
    quantity: Mapped[int]
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    taste_id: Mapped[int] = mapped_column(ForeignKey('tastes.id'))
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    tastes: Mapped[List['Taste'] | None] = relationship("Taste", back_populates="product")
    purchases: Mapped[List['Purchase']] = relationship("Purchase", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
class Taste(Base):
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    taste_name: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int]
    product: Mapped["Product"] = relationship("Product", back_populates="tastes")

    def __repr__(self):
        return f"<Taste(id={self.id}, taste_name='{self.taste_name}', quantity={self.quantity})>"


class Purchase(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    status: Mapped[str] = mapped_column(Text)
    user: Mapped["User"] = relationship("User", back_populates="purchases")
    product: Mapped["Product"] = relationship("Product", back_populates="purchases")

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, date={self.created_at})>"