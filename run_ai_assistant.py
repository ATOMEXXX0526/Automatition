#!/usr/bin/env python3
"""
Wrapper для запуска AI Assistant
"""
import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, '/home/user/Automatition')

# Устанавливаем переменные окружения по умолчанию
os.environ.setdefault('DRY_RUN_MODE', 'true')
os.environ.setdefault('FLASK_DEBUG', 'false')
os.environ.setdefault('LOG_FORMAT', 'text')  # Для лучшей читаемости

# Импортируем и запускаем
from ai_assistant.app.main import main

if __name__ == "__main__":
    main()
