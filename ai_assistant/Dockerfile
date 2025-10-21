FROM python:3.11-slim

# Метаданные
LABEL maintainer="AI Assistant for Naumen Service Desk"
LABEL version="1.0.0"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Загрузка NLTK данных
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Копирование проекта
COPY ../naumen_sdk /app/../naumen_sdk
COPY app /app/app
COPY models /app/models
COPY data /app/data
COPY scripts /app/scripts

# Создание директорий
RUN mkdir -p /app/models /app/logs

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.main

# Открываем порты
EXPOSE 5000 9090

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Запуск приложения
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app.main:app"]
