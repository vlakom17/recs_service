from pydantic import BaseModel, Field, UUID4
from typing import List
from datetime import datetime
from typing import Literal


class ItemBase(BaseModel):
    name: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., gt=0)
    item_category_id: int


class ItemDto(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)


class OrderBase(BaseModel):
    user_id: UUID4
    items: List[ItemDto]

# get order result
class OrderDto(OrderBase):
    order_id: UUID4
    status: Literal["CREATED", "CANCELLED", "DELIVERED"]
    creation_time: datetime


class recommendBase(BaseModel):
    user_id: UUID4
    items: List[ItemDto]


# create recommend
class CreaterecommendDto(recommendBase):
    pass


# update recommend
class UpdaterecommendDto(BaseModel):
    recommend_id: UUID4


# get recommend result
class recommendDto(recommendBase):
    recommend_id: UUID4
    creation_time: datetime
