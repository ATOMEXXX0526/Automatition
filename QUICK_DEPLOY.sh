#!/bin/bash
# Быстрое развертывание AI Assistant на сервере

set -e

echo "=========================================="
echo "AI Assistant - Быстрое развертывание"
echo "=========================================="
echo ""

# Проверка аргументов
if [ -z "$1" ]; then
    echo "Использование: ./QUICK_DEPLOY.sh [server_address]"
    echo "Пример: ./QUICK_DEPLOY.sh user@192.168.1.100"
    exit 1
fi

SERVER=$1
REMOTE_PATH="/opt/ai-assistant"

echo "Сервер: $SERVER"
echo "Путь на сервере: $REMOTE_PATH"
echo ""

# Шаг 1: Создание архива
echo "1. Создание архива проекта..."
tar -czf /tmp/ai-assistant-deploy.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='*.log' \
    ai_assistant/ \
    naumen_sdk/ \
    automation/ \
    run_ai_assistant.py \
    test_classifier_direct.py \
    config.py.example \
    requirements.txt \
    README.md \
    DEPLOYMENT.md

echo "✓ Архив создан: /tmp/ai-assistant-deploy.tar.gz"
echo ""

# Шаг 2: Загрузка на сервер
echo "2. Загрузка на сервер..."
scp /tmp/ai-assistant-deploy.tar.gz $SERVER:/tmp/
echo "✓ Файлы загружены"
echo ""

# Шаг 3: Развертывание на сервере
echo "3. Развертывание на сервере..."
ssh $SERVER << 'ENDSSH'
set -e

# Создание директории
sudo mkdir -p /opt/ai-assistant
sudo chown $USER:$USER /opt/ai-assistant
cd /opt/ai-assistant

# Распаковка
tar -xzf /tmp/ai-assistant-deploy.tar.gz
rm /tmp/ai-assistant-deploy.tar.gz

# Установка зависимостей
echo "Установка Python зависимостей..."
pip3 install --user -r requirements.txt || pip install --user -r requirements.txt

# Создание .env
if [ ! -f ai_assistant/.env ]; then
    cp config.py.example config.py
    echo ""
    echo "⚠️  ВНИМАНИЕ: Отредактируйте config.py с вашими настройками Naumen!"
    echo ""
fi

# Обучение модели
echo "Обучение ML модели..."
python3 ai_assistant/scripts/train_model.py

echo ""
echo "=========================================="
echo "✅ Развертывание завершено!"
echo "=========================================="
echo ""
echo "Проект установлен в: /opt/ai-assistant"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте config.py с настройками Naumen"
echo "2. Запустите сервер:"
echo "   cd /opt/ai-assistant"
echo "   export PYTHONPATH=/opt/ai-assistant"
echo "   python3 run_ai_assistant.py"
echo ""
echo "Или настройте systemd сервис (см. DEPLOYMENT.md)"
echo ""
ENDSSH

echo ""
echo "=========================================="
echo "✅ Готово!"
echo "=========================================="
echo ""
echo "Подключитесь к серверу:"
echo "  ssh $SERVER"
echo ""
echo "И запустите AI Assistant:"
echo "  cd /opt/ai-assistant"
echo "  export PYTHONPATH=/opt/ai-assistant"
echo "  python3 run_ai_assistant.py"
echo ""
echo "Подробная инструкция: DEPLOYMENT.md"
echo ""
