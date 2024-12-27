import aio_pika
import asyncio
import csv

# Функция для записи данных в CSV файл
def write_to_csv(item_data: dict):
    """Записывает данные о товаре в CSV файл"""
    file_path = 'routes/csv/items.csv'

    # Проверяем, существует ли файл, если нет, то добавляем заголовок
    try:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["item_name", "item_id", "item_category_id"])
            # Если файл пустой, записываем заголовок
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(item_data)
    except Exception as e:
        print(f"Ошибка при записи в CSV: {e}")


async def process_message(message: str):
    """Бизнес-логика обработки сообщений"""
    # Предположим, что сообщение — это строка JSON
    item_data = parse_message(message)
    
    # Записываем полученные данные в CSV
    write_to_csv(item_data)

def parse_message(message: str):
    """Парсинг сообщения, полученного через RabbitMQ (например, JSON)"""
    import json
    try:
        # Преобразуем строку JSON в словарь
        data = json.loads(message)
        item_data = {
            "item_name": data.get("name"),
            "item_id": data.get("item_id"),
            "item_category_id": data.get("item_category_id")
        }
        return item_data
    except Exception as e:
        print(f"Ошибка при парсинге сообщения: {e}")
        return {}


