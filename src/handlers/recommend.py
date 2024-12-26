import csv
import uuid
from datetime import datetime
from typing import List
from src.schemas.recommend import *
from src.schemas.result import GenResult, Error
from abc import ABC, abstractmethod

class recommendHandlerABC(ABC):
    @abstractmethod
    async def create_recommend(self, recommend: CreaterecommendDto) -> GenResult[None]:
        pass

    @abstractmethod
    async def get_recommend(self, recommend_id: uuid) -> GenResult[recommendDto]:
        pass

    @abstractmethod
    async def get_user_recommend(self, user_id: uuid) -> GenResult[List[recommendDto]]:
        pass

    @abstractmethod
    async def update_status(self, recommend_dto: UpdaterecommendDto) -> GenResult[None]:
        pass

class recommendHandler(recommendHandlerABC):
    def __init__(self):
        pass
