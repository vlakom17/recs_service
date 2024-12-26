import uuid
import csv
from typing import List
from src.schemas.recommend import CreaterecommendDto, recommendDto
from abc import ABC, abstractmethod

class recommendRepositoryABC(ABC):
    @abstractmethod
    async def get_by_user(self, *, user_id: uuid):
        """
        Получает все заказы пользователя с таким user_id.
        """
        pass


class recommendRepository(recommendRepositoryABC):
    def __init__(self, file_path: str):
        self.file_path = file_path




