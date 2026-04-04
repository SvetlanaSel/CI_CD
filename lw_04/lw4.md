# Лабораторная работа №4.1. Создание и развертывание полнофункционального аналитического приложения. Вариант 13


## Цель работы
Применить полученные знания по созданию и развертыванию трехзвенного приложения (Frontend + Backend + Database) в кластере Kubernetes. Научиться организовывать взаимодействие между микросервисами.

Задача:

| Вариант | Название системы | Бизнес-задача | Данные (Пример) |
|:-------:|:----------------|:--------------|:----------------|
| **13** | **Feedback System** | Сбор обратной связи от клиентов | • Оценка (1-5)<br>• Комментарий<br>• ID услуги<br>• Дата |

## Необходимые инструменты и технологии

*   **Язык программирования:** Python.
*   **Технологический стек :**
    *   **Backend:** FastAPI (современный, быстрый фреймворк для API).
    *   **Frontend:** Streamlit (библиотека для быстрого создания Data-интерфейсов).
    *   **Database:** PostgreSQL (реляционная БД)
*   **Инструменты:** Docker, Kubernetes (kubectl), Git.
*   **Репозиторий:** GitHub или GitVerse.

## Ход работы (Пример. Аналитический портал продаж)

**Сценарий.** Приложение для ввода отзывов об услугах компании, их просмотра и аналитики.
*   **DB:** PostgreSQL.
*   **Backend:** FastAPI.
*   **Frontend:** Streamlit.
---

### Шаг 1. Подготовка структуры

Архитектура проекта:
```
feedback-analytics/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── k8s/
│   ├── postgres.yaml
│   ├── backend.yaml
└── └── frontend.yaml
```
### Шаг 2. Разработка Бэкенда (FastAPI)
В папке backend/ были созданы файлы:

1. Dockerfile
```
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
2. requirements.txt
```
fastapi
uvicorn[standard]
psycopg2-binary
sqlalchemy
pydantic
```
3. main.py
```
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime
import time

# Ожидание запуска PostgreSQL в Kubernetes
time.sleep(6)

DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_NAME = os.getenv("DB_NAME", "feedback_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    service_id = Column(String, index=True, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Feedback Analytics API")

# Pydantic модели
class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: str | None = None
    service_id: str

class FeedbackResponse(FeedbackCreate):
    id: int
    date: datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/feedback")
def get_feedback(
    db: Session = Depends(get_db),
    service_id: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None)
):
    query = db.query(Feedback)
    if service_id:
        query = query.filter(Feedback.service_id == service_id)
    if start_date:
        query = query.filter(Feedback.date >= start_date)
    if end_date:
        query = query.filter(Feedback.date <= end_date)
    return query.all()

@app.post("/feedback", response_model=FeedbackResponse)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    new_feedback = Feedback(
        rating=feedback.rating,
        comment=feedback.comment,
        service_id=feedback.service_id
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Feedback).count()
    avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 0.0
    return {
        "total_feedback": total,
        "average_rating": round(float(avg_rating), 2)
    }
```
### Шаг 3. Разработка Фронтенда (Streamlit)
В папке frontend/ были созданы файлы:
1. Dockerfile
```
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
2. requirements.txt
```
streamlit
requests
pandas
plotly
wordcloud
matplotlib
```
3. app.py
```
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
from datetime import datetime
import time

# Настройка страницы
st.set_page_config(
    page_title="Feedback Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")

# Стилизация
st.markdown("""
<style>
    .feedback-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #ff4b4b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .rating-high {
        color: #28a745;
        font-weight: bold;
    }
    .rating-low {
        color: #dc3545;
        font-weight: bold;
    }
    .service-tag {
        background-color: #e9ecef;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        display: inline-block;
    }
    .comment-text {
        margin-top: 10px;
        padding: 10px;
        background-color: white;
        border-radius: 8px;
        font-style: italic;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
    }
    .wordcloud-container {
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Функции для работы с API
def get_all_feedback():
    try:
        response = requests.get(f"{BACKEND_URL}/feedback")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def add_feedback(rating, comment, service_id):
    try:
        response = requests.post(f"{BACKEND_URL}/feedback", json={
            "rating": rating,
            "comment": comment,
            "service_id": service_id
        })
        return response.status_code == 200
    except:
        return False

def get_stats():
    try:
        response = requests.get(f"{BACKEND_URL}/stats")
        if response.status_code == 200:
            return response.json()
        return {"total_feedback": 0, "average_rating": 0}
    except:
        return {"total_feedback": 0, "average_rating": 0}

# Инициализация состояния сессии
if 'show_form' not in st.session_state:
    st.session_state.show_form = False
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

# Боковая панель навигации
with st.sidebar:
    st.title("📊 Меню")
    page = st.radio(
        "Навигация",
        ["✍️ Написать отзыв", "📋 Все отзывы", "📈 Аналитика"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Feedback Analytics System v2.0")

# Страница 1: Написание отзыва
if page == "✍️ Написать отзыв":
    st.title("✍️ Написать новый отзыв")
    st.markdown("Поделитесь своим мнением о качестве обслуживания")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not st.session_state.show_form:
            if st.button("📝 Написать отзыв", type="primary", use_container_width=True):
                st.session_state.show_form = True
                st.rerun()
        
        if st.session_state.show_form:
            with st.form("feedback_form", clear_on_submit=True):
                st.subheader("Форма обратной связи")
                
                service_id = st.text_input("ID услуги", placeholder="Например: service-001")
                rating = st.slider("Оценка", min_value=1, max_value=5, value=5, 
                                   help="1 - очень плохо, 5 - отлично")
                comment = st.text_area("Комментарий", placeholder="Расскажите подробнее о вашем опыте...", height=150)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("✅ Отправить отзыв", use_container_width=True)
                with col_btn2:
                    if st.form_submit_button("❌ Отмена", use_container_width=True):
                        st.session_state.show_form = False
                        st.rerun()
                
                if submitted:
                    if service_id:
                        if add_feedback(rating, comment, service_id):
                            st.success("✅ Отзыв успешно добавлен! Спасибо за обратную связь!")
                            st.session_state.show_form = False
                            st.session_state.refresh = True
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Ошибка при добавлении отзыва")
                    else:
                        st.warning("⚠️ Пожалуйста, укажите ID услуги")
            
            with col2:
                st.info("💡 **Совет:**\n\n- Укажите конкретный ID услуги\n- Будьте объективны в оценке\n- Детальные комментарии помогают нам стать лучше")

# Страница 2: Просмотр всех отзывов
elif page == "📋 Все отзывы":
    st.title("📋 Все отзывы клиентов")
    
    # Кнопки фильтрации
    col_filter1, col_filter2 = st.columns([1, 1])
    with col_filter1:
        rating_filter = st.selectbox(
            "Фильтр по оценке", 
            ["Все", "⭐⭐⭐⭐⭐ 5", "⭐⭐⭐⭐ 4", "⭐⭐⭐ 3", "⭐⭐ 2", "⭐ 1"]
        )
    with col_filter2:
        sort_by = st.selectbox(
            "Сортировка", 
            ["По дате (новые)", "По дате (старые)", "По оценке (высокие)", "По оценке (низкие)"]
        )
    
    # Загрузка данных
    feedbacks = get_all_feedback()
    
    if feedbacks:
        # Применение фильтров
        if rating_filter != "Все":
            rating_value = {
                "⭐⭐⭐⭐⭐ 5": 5,
                "⭐⭐⭐⭐ 4": 4,
                "⭐⭐⭐ 3": 3,
                "⭐⭐ 2": 2,
                "⭐ 1": 1
            }[rating_filter]
            feedbacks = [f for f in feedbacks if f['rating'] == rating_value]
        
        # Применение сортировки
        if sort_by == "По дате (новые)":
            feedbacks.sort(key=lambda x: x['date'], reverse=True)
        elif sort_by == "По дате (старые)":
            feedbacks.sort(key=lambda x: x['date'])
        elif sort_by == "По оценке (высокие)":
            feedbacks.sort(key=lambda x: x['rating'], reverse=True)
        elif sort_by == "По оценке (низкие)":
            feedbacks.sort(key=lambda x: x['rating'])
        
        st.markdown(f"### Найдено отзывов: {len(feedbacks)}")
        
        # Отображение отзывов в виде карточек
        cols = st.columns(2)
        for idx, feedback in enumerate(feedbacks):
            with cols[idx % 2]:
                rating_class = "rating-high" if feedback['rating'] >= 4 else "rating-low" if feedback['rating'] <= 2 else ""
                
                stars = "⭐" * feedback['rating']
                date_obj = datetime.fromisoformat(feedback['date'].replace('Z', '+00:00'))
                formatted_date = date_obj.strftime("%d.%m.%Y %H:%M")
                
                st.markdown(f"""
                <div class="feedback-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="service-tag">📌 {feedback['service_id']}</span>
                        </div>
                        <div>
                            <span class="{rating_class}">{stars}</span>
                        </div>
                    </div>
                    <div class="comment-text">
                        💬 {feedback['comment'] if feedback['comment'] else "Нет комментария"}
                    </div>
                    <div style="margin-top: 10px; font-size: 12px; color: #6c757d;">
                        🕒 {formatted_date}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📭 Пока нет отзывов. Напишите первый отзыв!")

# Страница 3: Аналитика
elif page == "📈 Аналитика":
    st.title("📈 Аналитика обратной связи")
    
    # Загрузка данных
    feedbacks = get_all_feedback()
    stats = get_stats()
    
    if feedbacks:
        df = pd.DataFrame(feedbacks)
        df['date'] = pd.to_datetime(df['date'])
        
        # KPI карточки
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>📊 {stats['total_feedback']}</h3>
                <p>Всего отзывов</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <h3>⭐ {stats['average_rating']:.2f}</h3>
                <p>Средний рейтинг</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            positive = len(df[df['rating'] >= 4])
            st.markdown(f"""
            <div class="kpi-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <h3>😊 {positive}</h3>
                <p>Положительных (4-5⭐)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            negative = len(df[df['rating'] <= 2])
            st.markdown(f"""
            <div class="kpi-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <h3>😞 {negative}</h3>
                <p>Отрицательных (1-2⭐)</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Графики
        tab1, tab2, tab3 = st.tabs(["📊 Рейтинг по услугам", "🥧 Распределение оценок", "☁️ Облако слов"])
        
        with tab1:
            # Группировка по service_id (строковый тип)
            avg_rating = df.groupby("service_id")["rating"].mean().reset_index()
            avg_rating = avg_rating.sort_values("rating", ascending=False)
            fig = px.bar(avg_rating, x="service_id", y="rating", 
                        color="rating", color_continuous_scale="Viridis",
                        title="Средний рейтинг по услугам",
                        labels={"service_id": "ID услуги", "rating": "Средний рейтинг"})
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            rating_counts = df["rating"].value_counts().sort_index()
            fig = px.pie(values=rating_counts.values, names=rating_counts.index, 
                        title="Распределение оценок",
                        color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            if df["comment"].notna().any():
                text = " ".join(df["comment"].dropna().astype(str))
                if text.strip():
                    # Создаем колонки для центрирования облака слов
                    col_wc1, col_wc2, col_wc3 = st.columns([1, 2, 1])
                    with col_wc2:
                        wc = WordCloud(width=600, height=400, 
                                      background_color="white",
                                      colormap="viridis",
                                      max_words=100).generate(text)
                        fig, ax = plt.subplots(figsize=(8, 5))
                        ax.imshow(wc, interpolation="bilinear")
                        ax.axis("off")
                        st.pyplot(fig)
                else:
                    st.info("💬 Комментарии отсутствуют для создания облака слов")
            else:
                st.info("💬 Нет комментариев для анализа")
        
        # Кнопка экспорта
        st.markdown("---")
        col_export1, col_export2, col_export3 = st.columns([1, 2, 1])
        with col_export2:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Скачать все данные в CSV",
                data=csv,
                file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("📊 Нет данных для аналитики. Добавьте первые отзывы!")
```
### Шаг 4. Сборка образов

В терминале соберите образы (находясь в папках backend и frontend соответственно):
```bash
# В папке backend
docker build -t feedback-backend:v1 .

# В папке frontend
docker build -t feedback-frontend:v1 .
```
Результат:

<img width="1098" height="632" alt="image" src="https://github.com/user-attachments/assets/01c1ffcb-cb73-470b-9023-08fb7d933fb9" />

<img width="763" height="37" alt="image" src="https://github.com/user-attachments/assets/666e9799-5d82-4f45-a4f7-88efea9632d5" />

### Шаг 5. Манифесты Kubernetes
В папке `k8s` 
1. postgres.yaml
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          value: "user"
        - name: POSTGRES_PASSWORD
          value: "password"
        - name: POSTGRES_DB
          value: "feedback_db"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432

```
2. backend.yaml
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: feedback-backend:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: DB_USER
          value: "user"
        - name: DB_PASSWORD
          value: "password"
        - name: DB_NAME
          value: "feedback_db"
        ports:
        - containerPort: 8000

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000

```
3. frontend.yaml
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: feedback-frontend:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: BACKEND_URL
          value: "http://backend-service:8000"
        ports:
        - containerPort: 8501

---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 8501
    nodePort: 30080

```
### Шаг 6. Развертывание и тест
1.  Применю конфигурацию:
    ```bash
    kubectl apply -f k8s/
    ```
2.  Проверяю поды:
    ```bash
    kubectl get pods
    ```
    
<img width="627" height="236" alt="image" src="https://github.com/user-attachments/assets/397035c2-8e50-4bb4-a91f-7992b8c4e2b2" />

3.  Открою приложение: `http://localhost:30080`

<img width="1406" height="362" alt="image" src="https://github.com/user-attachments/assets/c0305955-2996-4aa1-ad34-406de9a0892f" />

<img width="1496" height="575" alt="image" src="https://github.com/user-attachments/assets/75a2db19-1f9f-44d7-ba2f-d2d6d6437467" />

<img width="1937" height="628" alt="image" src="https://github.com/user-attachments/assets/cc23e0e6-47f2-4f8d-aba7-f49ce16bf48c" />

<img width="1951" height="825" alt="image" src="https://github.com/user-attachments/assets/6a0bc218-5c46-4cab-8a21-9bef29b90bac" />

<img width="1697" height="771" alt="image" src="https://github.com/user-attachments/assets/2eb14984-db31-4042-a20c-2977c182bbc4" />

<img width="1702" height="943" alt="image" src="https://github.com/user-attachments/assets/2f0b06ab-844d-482d-97d8-d8b6116bd6ed" />

---

## Вывод

Разработана система сбора обратной связи Feedback System (вариант 13), реализующая полный цикл работы с отзывами клиентов: добавление, хранение, просмотр и аналитику. Приложение развернуто в Kubernetes, предоставляет удобный интерфейс с визуализацией статистики (графики, KPI, облако слов) и поддерживает экспорт данных. Все бизнес-требования выполнены в полном объеме.


<img width="697" height="188" alt="image" src="https://github.com/user-attachments/assets/d4f3c4cb-b896-4c79-a6fb-5d63718fca9d" />

