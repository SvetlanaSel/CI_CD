#!/usr/bin/env python3
"""
Streamlit-приложение: Dashboard для анализа складских запасов.
Вариант: Склад / Управление запасами / Анализ остатков.
"""

import os

import pandas as pd
import plotly.express as px
import streamlit as st
import psycopg2
from sqlalchemy import create_engine

# --- Подключение к БД ---
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "inventory")
DB_USER = os.getenv("POSTGRES_USER", "inventory_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "1121")


@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    """Загрузка данных из PostgreSQL."""
    try:
        conn_string = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(conn_string)
        df = pd.read_sql("SELECT * FROM inventory;", engine)
        return df
    except Exception as e:
        st.error(f"Ошибка подключения к БД: {e}")
        return pd.DataFrame()


# --- Интерфейс ---
st.set_page_config(
    page_title="Складской учёт - Dashboard", 
    layout="wide"
)

st.title("Управление складскими запасами — Анализ остатков")

# Загрузка данных
try:
    df = load_data()
    if df.empty:
        st.warning("Нет данных для отображения. Убедитесь, что контейнер loader завершил загрузку.")
        st.stop()
except Exception as e:
    st.error(f"Не удалось подключиться к БД: {e}")
    st.info("Убедитесь, что контейнер loader завершил загрузку данных.")
    st.stop()

# --- Боковая панель с фильтрами ---
st.sidebar.header("Фильтры")

# Фильтр по категории
categories = ['Все'] + sorted(df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Категория товара", categories)

# Фильтр по поставщику
suppliers = ['Все'] + sorted(df["supplier"].unique().tolist())
selected_supplier = st.sidebar.selectbox("Поставщик", suppliers)

# Фильтр по сроку годности
expiry_filter = st.sidebar.radio(
    "Срок годности",
    ["Все товары", "Только с истекающим сроком (30 дней)", "Бессрочные"]
)

# Применяем фильтры
df_filtered = df.copy()

if selected_category != 'Все':
    df_filtered = df_filtered[df_filtered["category"] == selected_category]

if selected_supplier != 'Все':
    df_filtered = df_filtered[df_filtered["supplier"] == selected_supplier]

if expiry_filter == "Только с истекающим сроком (30 дней)":
    df_filtered = df_filtered[df_filtered["expiry_date"].notna()]
    df_filtered["expiry_date"] = pd.to_datetime(df_filtered["expiry_date"])
    thirty_days_later = pd.Timestamp.now() + pd.Timedelta(days=30)
    df_filtered = df_filtered[df_filtered["expiry_date"] <= thirty_days_later]
elif expiry_filter == "Бессрочные":
    df_filtered = df_filtered[df_filtered["expiry_date"].isna()]

# --- Основные метрики ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Всего SKU", f"{len(df_filtered):,}")

with col2:
    total_stock = df_filtered["stock_quantity"].sum()
    st.metric("Общий остаток", f"{total_stock:,} шт.")

with col3:
    avg_price = df_filtered["price_rub"].mean()
    st.metric("Средняя цена", f"{avg_price:,.0f} руб.")

with col4:
    unique_suppliers = df_filtered["supplier"].nunique()
    st.metric("Поставщиков", f"{unique_suppliers}")

st.markdown("---")

# --- Основной график (bar chart по заданию): Остатки по категориям ---
st.subheader("Остатки товаров по категориям")

category_stock = (
    df_filtered.groupby("category")["stock_quantity"]
    .sum()
    .reset_index()
    .sort_values("stock_quantity", ascending=False)
)

fig_main = px.bar(
    category_stock,
    x="category",
    y="stock_quantity",
    title="Распределение складских остатков по категориям",
    labels={"category": "Категория", "stock_quantity": "Остаток (шт.)"},
    color="stock_quantity",
    color_continuous_scale="Viridis",
    text_auto=True
)

fig_main.update_layout(
    xaxis_tickangle=-45,
    height=500,
    showlegend=False
)

fig_main.update_traces(textposition="outside")
st.plotly_chart(fig_main, use_container_width=True)

st.markdown("---")

# --- ПЕРВЫЙ ГРАФИК: Топ-10 товаров по остаткам (на всю ширину) ---
st.subheader("Топ-10 товаров по остаткам")

top_stock = (
    df_filtered.nlargest(10, "stock_quantity")[["product_name", "stock_quantity", "category"]]
    .sort_values("stock_quantity", ascending=True)
)

fig_top_stock = px.bar(
    top_stock,
    x="stock_quantity",
    y="product_name",
    orientation="h",
    title="Товары с наибольшим остатком",
    labels={"stock_quantity": "Остаток (шт.)", "product_name": "Товар"},
    color="category",
    color_discrete_sequence=px.colors.qualitative.Set3,
    text="stock_quantity"
)

fig_top_stock.update_layout(
    height=500,
    xaxis_title="Остаток (шт.)",
    yaxis_title=""
)

fig_top_stock.update_traces(textposition="outside")
st.plotly_chart(fig_top_stock, use_container_width=True)

st.markdown("---")

# --- ВТОРОЙ ГРАФИК: Топ-10 по скорости продаж (на всю ширину) ---
st.subheader("Топ-10 по скорости продаж")

top_sales = (
    df_filtered.nlargest(10, "sales_speed_per_day")[["product_name", "sales_speed_per_day", "category"]]
    .sort_values("sales_speed_per_day", ascending=True)
)

fig_top_sales = px.bar(
    top_sales,
    x="sales_speed_per_day",
    y="product_name",
    orientation="h",
    title="Товары с наибольшей скоростью продаж",
    labels={"sales_speed_per_day": "Скорость продаж (шт./день)", "product_name": "Товар"},
    color="category",
    color_discrete_sequence=px.colors.qualitative.Set3,
    text_auto='.2f'
)

fig_top_sales.update_layout(
    height=500,
    xaxis_title="Скорость продаж (шт./день)",
    yaxis_title=""
)

fig_top_sales.update_traces(textposition="outside")
st.plotly_chart(fig_top_sales, use_container_width=True)

st.markdown("---")

# --- Анализ по поставщикам ---
st.subheader("Анализ по поставщикам")

supplier_stats = (
    df_filtered.groupby("supplier")
    .agg({
        "sku": "count",
        "stock_quantity": "sum",
        "price_rub": "mean",
        "sales_speed_per_day": "mean"
    })
    .reset_index()
    .rename(columns={
        "sku": "Товаров",
        "stock_quantity": "Общий остаток",
        "price_rub": "Средняя цена",
        "sales_speed_per_day": "Ср. скорость продаж"
    })
    .sort_values("Общий остаток", ascending=False)
    .head(10)
)

fig_suppliers = px.bar(
    supplier_stats,
    x="supplier",
    y="Общий остаток",
    title="Топ-10 поставщиков по объёму запасов",
    labels={"supplier": "Поставщик", "Общий остаток": "Остаток (шт.)"},
    color="Средняя цена",
    color_continuous_scale="Blues"
)

fig_suppliers.update_layout(xaxis_tickangle=-45, height=400)
st.plotly_chart(fig_suppliers, use_container_width=True)

