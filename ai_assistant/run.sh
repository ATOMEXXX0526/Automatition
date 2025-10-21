#!/bin/bash
# Скрипт запуска AI Assistant

set -e

echo "=========================================="
echo "AI Assistant - Запуск сервера"
echo "=========================================="

# Загрузка переменных окружения
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Установка режима DRY_RUN по умолчанию (безопасно для тестирования)
export DRY_RUN_MODE=${DRY_RUN_MODE:-true}

echo "Режим работы: DRY_RUN_MODE=$DRY_RUN_MODE"
echo "Flask порт: ${FLASK_PORT:-5000}"
echo ""

# Запуск Flask приложения
cd ..
PYTHONPATH=. python3 ai_assistant/app/main.py
