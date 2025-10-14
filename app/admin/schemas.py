from pydantic import BaseModel, Field
from datetime import date, datetime

class ProductIDModel(BaseModel):
    id: int

class UserIDModel(BaseModel):
    telegram_id: int

class PurchaseDateModel(BaseModel):
    date:date

class PurchaseForDellModel(BaseModel):
    status:str

class PurchaseAdressModel(BaseModel):
    adress:str

class DeliveryData(BaseModel):
    adress:str = Field(...)

class ProductModel(BaseModel):
    name: str = Field(..., min_length=5)
    description: str = Field(..., min_length=5)
    price: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    quantity: int = Field(default=0, gt=0) 