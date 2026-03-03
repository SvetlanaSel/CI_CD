#!/usr/bin/env python3
"""
Генератор синтетических данных: Складской учёт / Inventory.
Вариант: Склад / Управление запасами / Анализ остатков и скорости продаж.

Запуск: python generate_data.py
Результат: data/inventory.csv
"""

import csv
import os
import random
from datetime import datetime, timedelta

SEED = 42
NUM_ROWS = 2_000
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "inventory.csv")

# --- Параметры генерации ---

# Категории товаров
CATEGORIES = [
    "Электроника", "Одежда", "Продукты питания", "Бытовая химия",
    "Косметика", "Канцтовары", "Инструменты", "Автотовары",
    "Спорттовары", "Товары для дома", "Зоотовары", "Книги"
]

# Поставщики
SUPPLIERS = [
    "ООО 'Поставщик+'", "АО 'Торговый дом'", "ИП Иванов", "Группа 'Мегаполис'",
    "Компания 'Логистик'", "ООО 'ИмпортТрейд'", "АО 'РегионСнаб'", "ТД 'Универсал'",
    "ООО 'ОптТорг'", "ИП Петрова", "ЗАО 'СкладСервис'", "Торговый дом 'Восточный'"
]

# Весовое распределение для скорости продаж (units per day)
# Большинство товаров продаются медленно, некоторые - быстро
SALES_SPEED_WEIGHTS = {
    0.1: 30,   # очень медленно
    0.5: 25,   # медленно
    1.0: 20,   # средне
    2.0: 15,   # быстро
    5.0: 8,    # очень быстро
    10.0: 2    # супер-быстро
}

random.seed(SEED)

def weighted_sales_speed() -> float:
    """Выбор скорости продаж с учётом весов."""
    speeds = list(SALES_SPEED_WEIGHTS.keys())
    weights = list(SALES_SPEED_WEIGHTS.values())
    return random.choices(speeds, weights=weights, k=1)[0]

def generate_expiry_date() -> str:
    """Генерация срока годности (для продуктов - короткий срок, для других - длинный)."""
    category = random.choice(CATEGORIES)
    
    if category == "Продукты питания":
        # Для продуктов - срок годности от 7 до 365 дней
        days = random.randint(7, 365)
    elif category in ["Косметика", "Бытовая химия"]:
        # Для косметики и химии - от 1 до 3 лет
        days = random.randint(365, 1095)
    else:
        # Для остальных товаров - от 2 до 5 лет или бессрочно (NULL)
        if random.random() < 0.3:  # 30% товаров бессрочные
            return "NULL"
        else:
            days = random.randint(730, 1825)
    
    expiry_date = datetime.now() + timedelta(days=days)
    return expiry_date.strftime("%Y-%m-%d")

def generate_sku(index: int) -> str:
    """Генерация уникального SKU."""
    letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    numbers = str(index).zfill(6)
    return f"{letters}-{numbers}"

def generate() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = [
        "sku",
        "product_name",
        "category",
        "supplier",
        "stock_quantity",
        "sales_speed_per_day",
        "expiry_date",
        "warehouse_location",
        "price_rub",
        "reorder_point"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, NUM_ROWS + 1):
            sku = generate_sku(i)
            category = random.choice(CATEGORIES)
            supplier = random.choice(SUPPLIERS)
            
            # Генерация остатка на складе (от 0 до 1000)
            stock_quantity = random.randint(0, 1000)
            
            # Скорость продаж в единицах в день
            sales_speed = weighted_sales_speed()
            
            # Срок годности
            expiry_date = generate_expiry_date()
            
            # Локация на складе
            warehouse_location = f"Ряд {random.randint(1, 20)}-Стеллаж {random.randint(1, 50)}"
            
            # Цена в рублях
            price_rub = round(random.uniform(50, 50000), 2)
            
            # Точка заказа (reorder point) - когда нужно заказывать новый товар
            reorder_point = int(sales_speed * random.randint(7, 30))  # от 7 до 30 дней продаж
            
            # Название товара
            product_names = {
                "Электроника": ["Смартфон", "Ноутбук", "Планшет", "Наушники", "Монитор"],
                "Одежда": ["Футболка", "Джинсы", "Куртка", "Платье", "Кроссовки"],
                "Продукты питания": ["Консервы", "Крупа", "Макароны", "Чай", "Кофе"],
                "Бытовая химия": ["Стиральный порошок", "Моющее средство", "Мыло", "Шампунь"],
                "Косметика": ["Крем", "Духи", "Тушь", "Помада", "Тональный крем"],
                "Канцтовары": ["Ручка", "Тетрадь", "Бумага", "Папка", "Степлер"],
                "Инструменты": ["Молоток", "Отвертка", "Дрель", "Пила", "Ключ"],
                "Автотовары": ["Масло", "Фильтр", "Шина", "Аккумулятор", "Дворники"],
                "Спорттовары": ["Мяч", "Гантели", "Коврик", "Велосипед", "Лыжи"],
                "Товары для дома": ["Подушка", "Одеяло", "Посуда", "Свеча", "Картина"],
                "Зоотовары": ["Корм", "Игрушка", "Поводок", "Клетка", "Лоток"],
                "Книги": ["Роман", "Словарь", "Энциклопедия", "Детектив", "Фантастика"]
            }
            
            product_name = f"{random.choice(product_names[category])} {random.choice(['A', 'B', 'C', 'Pro', 'Lite', 'Max'])}-{random.randint(1, 999)}"

            writer.writerow(
                {
                    "sku": sku,
                    "product_name": product_name,
                    "category": category,
                    "supplier": supplier,
                    "stock_quantity": stock_quantity,
                    "sales_speed_per_day": round(sales_speed, 2),
                    "expiry_date": expiry_date,
                    "warehouse_location": warehouse_location,
                    "price_rub": price_rub,
                    "reorder_point": reorder_point
                }
            )

    print(f"Сгенерировано {NUM_ROWS} записей → {OUTPUT_FILE}")


if __name__ == "__main__":
    generate()