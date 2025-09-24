from pydantic import BaseModel, ConfigDict, Field


class TelegramIDModel(BaseModel):
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)


class UserModel(TelegramIDModel):
    username: str | None
    first_name: str | None
    last_name: str | None


class ProductIDModel(BaseModel):
    id: int

class PurchaseIDModel(BaseModel):
    id: int

class ProductCategoryIDModel(BaseModel):
    category_id: int


class ItemCartData(BaseModel):
    user_id: int = Field(..., description="ID пользователя Telegram")
    product_id: int = Field(..., description="ID товара")
    status: str = Field(..., description="Статус товара")

class CartModel(BaseModel):
    id:int