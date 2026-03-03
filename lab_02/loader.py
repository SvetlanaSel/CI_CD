#!/usr/bin/env python3
"""
ETL-загрузчик: читает inventory.csv и загружает в PostgreSQL.
Запускается как init-контейнер (loader) после healthy-статуса БД.
"""

import csv
import os
import sys
import time

import psycopg2

# --- Настройки из переменных окружения ---
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "inventory")
DB_USER = os.getenv("POSTGRES_USER", "inventory_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "1121")
CSV_PATH = os.getenv("CSV_PATH", "/data/inventory.csv")

DDL = """
CREATE TABLE IF NOT EXISTS inventory (
    sku                   VARCHAR(20) PRIMARY KEY,
    product_name          VARCHAR(100) NOT NULL,
    category              VARCHAR(50) NOT NULL,
    supplier              VARCHAR(100) NOT NULL,
    stock_quantity        INTEGER NOT NULL,
    sales_speed_per_day   REAL NOT NULL,
    expiry_date           DATE,
    warehouse_location    VARCHAR(50) NOT NULL,
    price_rub             REAL NOT NULL,
    reorder_point         INTEGER NOT NULL
);
"""


def wait_for_db(max_retries: int = 30, delay: int = 2) -> psycopg2.extensions.connection:
    """Ожидание готовности PostgreSQL."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT,
                dbname=DB_NAME, user=DB_USER, password=DB_PASS,
            )
            print(f"[loader] БД доступна (попытка {attempt})")
            return conn
        except psycopg2.OperationalError:
            print(f"[loader] Ожидание БД... ({attempt}/{max_retries})")
            time.sleep(delay)
    print("[loader] БД недоступна, завершение.")
    sys.exit(1)


def load_csv(conn: psycopg2.extensions.connection) -> int:
    """Загрузка CSV в таблицу inventory."""
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM inventory;")
    if cur.fetchone()[0] > 0:
        print("[loader] Таблица уже содержит данные — пропуск загрузки.")
        return 0

    count = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Обработка NULL значения для expiry_date
            expiry_date = row["expiry_date"]
            if expiry_date == "NULL" or not expiry_date:
                expiry_date = None
                
            cur.execute(
                """
                INSERT INTO inventory
                    (sku, product_name, category, supplier, stock_quantity,
                     sales_speed_per_day, expiry_date, warehouse_location,
                     price_rub, reorder_point)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sku) DO NOTHING;
                """,
                (
                    row["sku"],
                    row["product_name"],
                    row["category"],
                    row["supplier"],
                    int(row["stock_quantity"]),
                    float(row["sales_speed_per_day"]),
                    expiry_date,
                    row["warehouse_location"],
                    float(row["price_rub"]),
                    int(row["reorder_point"])
                ),
            )
            count += 1

    conn.commit()
    cur.close()
    print(f"[loader] Загружено {count} строк в таблицу inventory.")
    return count


def main() -> None:
    conn = wait_for_db()
    try:
        load_csv(conn)
    finally:
        conn.close()
    print("[loader] Готово.")


if __name__ == "__main__":
    main()