import pandas as pd
import numpy as np
import datetime
from sklearn.metrics.pairwise import cosine_similarity
import random
from datetime import datetime

def read_data() -> pd.DataFrame:
    """
    Считывает и минимально преобразовывает тренировочную выборку
    
    :return: Тренировочную выборку
    """
    sales_train = pd.read_csv("src/routes/csv/sales_train.csv")
    
    sales_train = sales_train[sales_train['item_price'] > 0]
    sales_train = sales_train[sales_train['item_cnt_day'] > 0]

    sales_train['date'] = pd.to_datetime(sales_train['date'],format="%d.%m.%Y")

    return sales_train

def get_popular(sales_train:pd.DataFrame) -> pd.DataFrame:
    """
    :return: Отсортированный датафрейм по наиболее популярным товарам
    """
    
    # Группируем по товарам и считаем суммарное количество проданных единиц
    item_sales = sales_train.groupby('item_id').agg({'item_cnt_day': 'sum'}).reset_index()
    
    # Сортируем товары по убыванию количества проданных единиц
    popular_items = item_sales.sort_values(by='item_cnt_day', ascending=False)
    
    return popular_items

def prepare_data_for_season(sales_train:pd.DataFrame, user_history:list) -> pd.DataFrame:
    """
    Вычисляет косинусное сходство между товарами относительно сезонности
    
    :param sales_train: Тренировочная выборка
    :param user_history: История покупок пользователя
    :return: Датафрейм косинусных расстояний
    """
    # Добавляем признаки для анализа сезонности
    new_sales = sales_train
    new_sales['month'] = sales_train['date'].dt.month
    new_sales['day_of_week'] = sales_train['date'].dt.weekday  # Понедельник = 0, Воскресенье = 6
    new_sales['quarter'] = sales_train['date'].dt.quarter
    new_sales['year'] = sales_train['date'].dt.year

    # Агрегируем данные по товару и месяцу
    monthly_sales = new_sales.groupby(['item_id', 'month']).agg(
        monthly_sales=('item_cnt_day', 'sum')
    ).reset_index()

    # Создаем матрицу продаж с учетом сезонности
    interaction_matrix_seasonal = new_sales.pivot_table(
        index='item_id', 
        columns='month', 
        values='item_cnt_day', 
        aggfunc='sum', 
        fill_value=0
    )

    items_bought = new_sales.groupby('item_id')['item_cnt_day'].agg('sum')
    mask = items_bought[(items_bought > 50) | (items_bought.index.isin(user_history))].index

    interaction_matrix_seasonal = interaction_matrix_seasonal.loc[mask,:]

    # Вычисляем косинусное сходство между товарами
    cosine_sim = cosine_similarity(interaction_matrix_seasonal.fillna(0))

    # Создаем DataFrame для удобства
    cosine_sim_df = pd.DataFrame(cosine_sim, index=interaction_matrix_seasonal.index, columns=interaction_matrix_seasonal.index)
    
    return cosine_sim_df

def prepare_data_for_category(sales_train:pd.DataFrame,items:pd.DataFrame,user_history:list) -> pd.DataFrame:
    """
    Вычисляет косинусное сходство между товарами относительно категорий
    
    :param sales_train: Тренировочная выборка
    :param user_history: История покупок пользователя
    :return: Датафрейм косинусных расстояний
    """
    sales_with_categ = pd.merge(sales_train,items[['item_id','item_category_id']],how='inner') 
    
    # Агрегируем данные по категории
    category_sales = sales_with_categ.groupby(['item_id', 'item_category_id']).agg(
        categ_sales=('item_cnt_day', 'sum')
    ).reset_index()

    # Создаем матрицу продаж с учетом категории
    interaction_matrix_categorial = sales_with_categ.pivot_table(
        index='item_id', 
        columns='item_category_id', 
        values='item_cnt_day', 
        aggfunc='sum', 
        fill_value=0
    )

    items_bought = sales_with_categ.groupby('item_id')['item_cnt_day'].agg('sum')
    mask = items_bought[(items_bought > 50) | (items_bought.index.isin(user_history))].index

    interaction_matrix_categorial = interaction_matrix_categorial.loc[mask,:]

    # Вычисляем косинусное сходство между товарами
    cosine_sim = cosine_similarity(interaction_matrix_categorial.fillna(0))
    
    # Создаем DataFrame для удобства
    cosine_sim_df = pd.DataFrame(cosine_sim, index=interaction_matrix_categorial.index, columns=interaction_matrix_categorial.index)

    return cosine_sim_df

def prepare_data_for_user(sales_prod:pd.DataFrame,user_history:list) -> pd.DataFrame:
    """
    Вычисляет косинусное сходство между товарами относительно других пользователей
    
    :param sales_train: Тренировочная выборка
    :param user_history: История покупок пользователя
    :return: Датафрейм косинусных расстояний
    """
    # Агрегируем данные по user_id
    user_sales = sales_prod.groupby(['item_id', 'user_id']).agg(
        user_sales=('item_cnt_day', 'sum')
    ).reset_index()


    # Создаем матрицу продаж с учетом других пользователей
    interaction_matrix_user = user_sales.pivot_table(
        index='item_id', 
        columns='user_id', 
        values='item_cnt_day', 
        aggfunc='sum', 
        fill_value=0
    )

    items_bought = user_sales.groupby('item_id')['item_cnt_day'].agg('sum')
    mask = items_bought[(items_bought > 50) | (items_bought.index.isin(user_history))].index

    interaction_matrix_user = interaction_matrix_user.loc[mask,:]

    # Вычисляем косинусное сходство между товарами
    cosine_sim = cosine_similarity(interaction_matrix_user.fillna(0))
    
    # Создаем DataFrame для удобства
    cosine_sim_df = pd.DataFrame(cosine_sim, index=interaction_matrix_user.index, columns=interaction_matrix_user.index)

    return cosine_sim_df

def get_similar_items(item_id:int,cosine_sim_df:pd.DataFrame, top_n=10) -> pd.DataFrame:
    """
    Находит самые похожие товары
    
    :param item_id: Идентификатор товара
    :param cosine_sim_df: Косинусные расстояния
    :param top_n: Количество товаров, которое хотим рекомендовать
    :return: Самые похожие товары
    """
    # Получаем сходство для указанного товара
    similar_items = cosine_sim_df[item_id].sort_values(ascending=False).head(top_n+1)
    
    # Возвращаем рекомендованные товары (исключая сам товар)
    return similar_items.index[1:]

def recommend_seasons_items(user_id:int, user_history:list, top_n=10) -> list:
    """
    Рекомендует список товаров пользователю относительно его истории покупок.
    Если пользователь новый, то рекомендует топ самых популярных товаров.
    Иначе делит пользователей на группы следующим образом:
    - если история покупок пользователей на нашем сервисе небольшая, то делит на 2 группы
    - иначе делит на 3 группы
    
    0-я группа - топ популярных товаров
    1-я группа - рекомендации по сезонности
    2-я группа - рекомендации по категориям
    3-я группа - рекомендации относительно покупок других юзеров.
    Далее, добавляет данные в табличку всех рекомендаций для дальнейшего сравнения эффективности каждой группы рекомендаций.

    :param user_id: Идентификатор пользователя
    :param user_history: История покупок пользователя
    :param top_n: Сколько товаров хотим порекомендовать
    :return: Список рекомендаций
    """
    
    sales_train = read_data() # Чтение обучающей выборки
    
    popular_items = get_popular(sales_train) # Датафрейм с самыми популярными товарами
    
    all_recommendations = pd.read_csv("src/routes/csv/all_recomendations.csv") # Датафрейм с информацией об истории рекомендаций пользователям
    
    items = pd.read_csv("src/routes/csv/items.csv") # Таблица для получения категорий товаров

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Время рекомендации

    bucket_id = 0 # Группа разбиения
    
    if not user_history:  # Если у пользователя нет истории покупок
        # Рекомендуем самые популярные товары
        recommendation_list = popular_items.head(top_n)['item_id'].tolist()
        
        # Добавление данных о новой рекомендации
        new_row = {'data':now,'user_id':user_id,'recommendations':recommendation_list,'bucket_id':bucket_id}
        row_to_append = pd.DataFrame(new_row)
        all_recommendations = pd.concat([all_recommendations,row_to_append],ignore_index=True)
        
        return recommendation_list
    else:
        # Для пользователей с историей покупок рекомендуем товары по схожести
        
        sales_prod = pd.read_csv('src/routes/csv/sales_prod.csv') # История покупок на нашем сервисе
        
        if(len(sales_prod) < 10):
            bucket_id = random.randint(1, 2)
        else:
            bucket_id = random.randint(1, 3)

        
        if bucket_id == 1: 
            # Сезонность
            cosine_sim_df = prepare_data_for_season(sales_train,user_history)
        elif bucket_id == 2:
            # Категории
            cosine_sim_df = prepare_data_for_category(sales_train,items,user_history)
        elif bucket_id == 3:
            # Пользователи
            cosine_sim_df = prepare_data_for_user(sales_prod)
        else:
            recommendation_list = popular_items.head(top_n)['item_id'].tolist()

            # Добавление данных о новой рекомендации
            new_row = {'data':now,'user_id':user_id,'recommendations':recommendation_list,'bucket_id':0}
            row_to_append = pd.DataFrame(new_row)
            all_recommendations = pd.concat([all_recommendations,row_to_append],ignore_index=True)
            
            return recommendation_list

            
        recommended_items = set()
        
        for item in user_history:
            similar_items = get_similar_items(item,cosine_sim_df, top_n)
            recommended_items.update(similar_items)
          
        recommendation_list = list(recommended_items)[:top_n]

        # Добавление данных о новой рекомендации
        new_row = {'data':now,'user_id':user_id,'recommendations':recommendation_list,'bucket_id':bucket_id}
        row_to_append = pd.DataFrame(new_row)
        all_recommendations = pd.concat([all_recommendations,row_to_append],ignore_index=True)

        return recommendation_list