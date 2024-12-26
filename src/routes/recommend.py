from fastapi import APIRouter, Depends, HTTPException, Query
from http import HTTPStatus
from src.handlers.recommend import recommendHandlerABC
from src.schemas.recommend import *
from .recommendation_system import recommend_seasons_items

from src.schemas.result import RecommendationResponse, RecommendationRequest
from .predict_price import forecast_price1

router = APIRouter()

@router.get("/ping")
def ping_pong():
    return "pong"


@router.post("/model/recommendation/", response_model=RecommendationResponse)
def get_recommendations(request: RecommendationRequest):
    """
    Эндпоинт для получения списка рекомендаций для пользователя.
    
    Тело запроса:
    - user_id: уникальный идентификатор пользователя (UUID)
    
    Ответ:
    - recommended_products: список рекомендованных товаров (ID товаров в виде строк)
    """
    try:
        # Генерация рекомендаций
        # Временно используем пустую историю покупок для всех пользователей
        user_history = []  # В реальном случае здесь можно подтянуть историю покупок по user_id
        top_n = 10  # Вы можете изменить это значение на ваше усмотрение
        
        # Получаем рекомендации
        recommendation_list = recommend_seasons_items(
            user_id=request.user_id,
            user_history=user_history,
            top_n=top_n
        )
        
        # Преобразуем рекомендации в строковый формат
        recommendation_list = [str(item) for item in recommendation_list]
        
        # Возвращаем результат
        return RecommendationResponse(recommended_products=recommendation_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/predict")
async def predict_price(item_id: int = Query(..., description="ID товара для предсказания цены")):
    """
    Эндпоинт для предсказания цены товара.
    """
    try:
        # Вызов функции прогнозирования цены
        predicted_price = forecast_price1(item_id)
        if predicted_price == -1:
            raise HTTPException(status_code=404, detail="Нет данных для данного товара")
        
        return {
            "item_id": item_id,
            "predicted_price": round(predicted_price, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
