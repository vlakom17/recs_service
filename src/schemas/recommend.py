from pydantic import BaseModel, Field, UUID4
from typing import List
from datetime import datetime

class ItemDto(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)


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
