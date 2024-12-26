import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
from statsmodels.tsa.stattools import adfuller

def read_data() -> pd.DataFrame:
  """
  Возвращает данные для прогноза
  """
  sales_train = pd.read_csv("csv.sales_train.csv")
  
  sales_train = sales_train[sales_train['item_price'] > 0]
  sales_train = sales_train[sales_train['item_cnt_day'] > 0]
  
  # Преобразуем колонку date в тип datetime
  sales_train['date'] = pd.to_datetime(sales_train['date'],format = "%d.%m.%Y")
  
  # Сортируем данные по дате и item_id
  sales_train = sales_train.sort_values(by=['item_id', 'date'])
  
  # Группируем данные по item_id и дате, чтобы получить среднюю цену за день
  sales_train_grouped = sales_train.groupby(['item_id', 'date']).agg({'item_price': 'median'}).reset_index()
  
  return sales_train_grouped

def test_stationarity(series:pd.Series) -> int:
  """
  Проверяет ряд на стационарность

  :param series: Временной ряд
  :return: 1 если ряд стационарен, 0 иначе
  """
  result = adfuller(series, autolag='AIC')
  flag = 0
  
  if result[1] > 0.05:
    return 0
  else:
    return 1

def make_stationary(item_data_interpolated:pd.Series) -> pd.Series:
  """
  Интегрирует ряд, для того, чтобы сделать его стационарным

  :param item_data_interpolated: Временной ряд
  :return: Интегрированный временной ряд
  """
  df = pd.DataFrame({'date':item_data_interpolated.index,'item_price':item_data_interpolated.values})
  df['item_price'] = df['item_price'] - df['item_price'].shift(1)
  
  df = df.dropna()
  df = df.set_index('date')['item_price']
  
  return df

def forecast_price1(item_id:int) -> float:
  """
  Предсказывает цену товара

  :param item_id: Идентификатор товара
  :return: Предсказанную цену товара
  """
  
  sales_train_grouped = read_data()
  # Дата на которую нужно предсказание (текущий день)
  forecast_date = datetime.today().strftime('%Y-%m-%d')
  
  # Фильтруем данные для нужного товара
  item_data = sales_train_grouped[sales_train_grouped['item_id'] == item_id]
  
  if len(item_data) == 0:
    # Если ранее покупок не было, то выводим -1 (это временно, скоро исправим)
    return -1
  elif len(item_data) == 1:
    tmp = pd.DataFrame({'item_id':[item_id],'date':[pd.to_datetime(max(sales_train_grouped['date']))],'item_price':[item_data['item_price'].iloc[0]]})
    item_data = pd.concat([tmp,item_data])
  
  # Устанавливаем дату как индекс
  item_data = item_data.set_index('date')['item_price']
  
  # Пересемплирование данных для установки регулярного интервала
  item_data_resampled = item_data.resample('D').asfreq()
  
  # Заполнение пропущенных значений интерполяцией
  item_data_interpolated = item_data_resampled.interpolate(method ='linear')
  
  # Определение порядка интегрирования (d)
  tmp_stationarity = item_data_interpolated
  try:
    stationarity = test_stationarity(tmp_stationarity,'Price')
  except ValueError:
    stationarity = 1
    d = 0
  while (stationarity != 1):
    tmp_stationarity = make_stationary(tmp_stationarity)
    d += 1
    stationarity = test_stationarity(tmp_stationarity,'Price')
  
  # Строим модель ARIMA (p, d, q) для данного товара
  model = ARIMA(item_data_interpolated, order=(1, d, 7)) 
  model_fit = model.fit()
  
  item_data_interpolated = pd.DataFrame({'date':item_data_interpolated.index,'item_price':item_data_interpolated.values})

  # Последняя дата покупки товара
  last_date = item_data_interpolated.date.iloc[-1:].iloc[0].strftime("%Y-%m-%d")

  # Рассчитываем на сколько дней делается прогноз
  p_steps = (datetime.strptime(forecast_date,"%Y-%m-%d") - datetime.strptime(last_date,"%Y-%m-%d")).days
  
  # Делаем прогноз на будущее
  forecast = model_fit.forecast(steps=p_steps)
  
  forecast_future = model_fit.get_forecast(steps=p_steps)

  # Ограничиваем нижнюю грань цены в половину от минимальной (нужно для того, чтобы цена не уходила ниже 0)
  forecast = forecast.clip(lower=(min(sales_train_grouped[sales_train_grouped['item_id'] == item_id]['item_price']))*0.5).tolist()
  
  # Предположим, ожидаемая инфляция 4% в год
  annual_inflation_rate = 0.04
  
  # Корректируем прогноз с учетом инфляции
  months_ahead = len(forecast)
  inflation_adjusted_forecast = []
  
  for i in range(months_ahead):
      inflated_price = forecast[i] * (1 + annual_inflation_rate / 365) ** i
      inflation_adjusted_forecast.append(inflated_price)
  
  item_data_interpolated.set_index('date',inplace=True)
  
  # Создаем новый DataFrame для будущих значений
  future_dates = pd.date_range(start=str(last_date), periods=p_steps, freq='D') + pd.DateOffset(days=1)
  forecast_df = pd.DataFrame(data={'future_price': inflation_adjusted_forecast}, index=future_dates)
    
  return forecast_df['future_price'].iloc[-1]