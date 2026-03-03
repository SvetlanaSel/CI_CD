# Лабораторная работа 2.1. Создание Dockerfile и сборка образа для аналитических приложений. Вариант 13

## Цель работы
Научиться разрабатывать воспроизводимые аналитические инструменты. Студенту необходимо пройти полный цикл: от написания Python-скрипта для обработки бизнес-данных до его упаковки в Docker-образ и запуска в изолированной среде.

Данные:
| № Темы | Предметная область | Примерные поля данных |
| :---: | :--- | :--- |
| **3** | **Inventory / Склад** | SKU товара, остаток на складе, скорость продаж, срок годности, поставщик. |

Задание - 13 - Streamlit. Создать Dashboard на Streamlit. Отобразить заголовок и один график (bar chart) по вашим данным. Правильно настроить CMD и EXPOSE.

---
## Ход работы

### Этап 1. Генерация данных

Для начала создаю данные для анализа:

<img width="1182" height="797" alt="image" src="https://github.com/user-attachments/assets/6e0c3f8a-45d8-402e-bda6-18a8bd2ac4e1" />

Данные успешно сгенерированы и сохранены в файл:
- []()

Файл с кодом генерации:
- []()

### Этап 2. Образ Postgres


Меняю параметры файла .env:
```
# ==============================
# Переменные окружения проекта
# ==============================
POSTGRES_DB=inventory
POSTGRES_USER=inventory_user
POSTGRES_PASSWORD=1121
DB_HOST=db
DB_PORT=5432
```

### Этап 3. Файл загрузки

Создаю файл загрузки под свои данные и задачи:
- []()

### Этап 4. Файл визуализации и аналитики

Создаю файл для анализа и создания Dashboard на Streamlit
- []()

### Этап 5. Dockerfile

Создаю докер файл по своим параметрам:

```
# ============================================================
# Dockerfile — analytics_app (loader + dashboard)
# ============================================================

# 1. Конкретная версия slim-образа (не latest)
FROM python:3.10-slim

# 2. Метаданные
LABEL maintainer="student" \
      description="Inventory analytics: ETL loader + Streamlit dashboard"

# 3. Установка системных зависимостей + очистка кэша в одном слое
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 4. Создание непривилегированного пользователя (UID 1000)
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 -m appuser

# 5. Рабочая директория
WORKDIR /app

# 6. Копирование и установка зависимостей ДО кода (кэш слоёв)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Копирование кода приложения
COPY loader.py dashboard.py ./

# 8. Переключение на непривилегированного пользователя
USER appuser

# 9. Порт Streamlit
EXPOSE 8501

# 10. Точка входа по умолчанию — дашборд
CMD ["streamlit", "run", "dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]

```
- []()

### Этап 6. Docker compose

Совмещаю все файлы для запуска образа и проведения аналитики в файле:
- []()

Далее запускаю докер:

<img width="691" height="275" alt="image" src="https://github.com/user-attachments/assets/fe34db1e-db9e-4998-b6c4-b79f0f357b59" />

---

### Этап 7. Аналитика и визуализация. Переход на Streamlit

Открываю в браузере localhost, на нем запускается Streamlit

<img width="1215" height="738" alt="image" src="https://github.com/user-attachments/assets/4f915e05-58df-4893-96f1-02a303db23cf" />

<img width="810" height="561" alt="image" src="https://github.com/user-attachments/assets/3d2c9e13-51ad-48dd-a5ee-c98080ebf4b8" />

<img width="822" height="580" alt="image" src="https://github.com/user-attachments/assets/78b40632-3c13-43ce-8841-9f7885fbab93" />

<img width="788" height="494" alt="image" src="https://github.com/user-attachments/assets/333ab28f-9661-45b2-a010-e458740e4ab3" />

### Этап 8. Выключение докер

После выполнения работы завершаю запуск докер:

<img width="702" height="197" alt="image" src="https://github.com/user-attachments/assets/ab1ae061-9d48-4e3a-9eff-d2350910907f" />

---

## Вывод
