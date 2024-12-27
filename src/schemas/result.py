import dataclasses
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

ModelType = TypeVar("ModelType", bound=BaseModel)


class RecommendationRequest(BaseModel):
    user_id: str = Field(..., description="Уникальный идентификатор пользователя (UUID)")

class RecommendationResponse(BaseModel):
    recommended_products: List[str] = Field(..., description="Список рекомендованных товаров (ID товаров в виде строк)")

class PredictPriceRequest(BaseModel):
    item_id: int

@dataclasses.dataclass
class Error:
    reason: str
    code: str

@dataclasses.dataclass
class Result:
    is_success: bool
    error: Error | None
    
    @staticmethod
    def failure(error: Error):
        return Result(is_success=False, error=error)
    
    
    @staticmethod
    def success():
        return Result(is_success=True, error=None)
    

@dataclasses.dataclass
class GenResult(Result, Generic[ModelType]):
    response: ModelType | None
    is_success: bool
    error: Error | None
    
    
    @staticmethod
    def failure(error):
        return GenResult(is_success=False, error=error, response=None)
    
    
    @staticmethod
    def success(value: ModelType):
        return GenResult(is_success=True, error=None, response=value)
