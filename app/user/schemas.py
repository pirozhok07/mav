from pydantic import BaseModel, ConfigDict, Field


class TelegramIDModel(BaseModel):
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)


class UserModel(TelegramIDModel):
    username: str | None
    first_name: str | None
    last_name: str | None

class ProductUpdateIDModel(BaseModel):
    id: int

class ProductIDModel(BaseModel):
    id: int

class PurchaseIDModel(BaseModel):
    id: int

class PurchaseUserIDModel(BaseModel):
    user_id: int

class TasteIDModel(BaseModel):
    id: int

class ProductCategoryIDModel(BaseModel):
    category_id: int

class PurchaseModel(BaseModel):
    user_id: int
    status: str

class ItemCartData(BaseModel):
    user_id: int = Field(..., description="ID пользователя Telegram")
    goods_id: str = Field(..., description="ID товаров")
    total: int = Field(..., description="Цена товара")
    status: str = Field(..., description="Статус товара")

class CartModel(BaseModel):
    id:int