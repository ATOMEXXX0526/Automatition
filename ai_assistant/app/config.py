"""
AI Assistant Configuration
Загружает настройки из переменных окружения с дефолтными значениями
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (если существует)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = BASE_DIR / "ai_assistant" / ".env"
if env_file.exists():
    load_dotenv(env_file)

# ===========================
# Базовые пути
# ===========================
MODELS_DIR = BASE_DIR / "ai_assistant" / "models"
DATA_DIR = BASE_DIR / "ai_assistant" / "data"
LOGS_DIR = BASE_DIR / "ai_assistant" / "logs"

# Создаём директории, если не существуют
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Пути к файлам модели
MODEL_PATH = MODELS_DIR / "classifier_model.pkl"
VECTORIZER_PATH = MODELS_DIR / "vectorizer.pkl"

# ===========================
# Flask настройки
# ===========================
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# ===========================
# Naumen Service Desk настройки
# ===========================
NAUMEN_URL = os.getenv("NAUMEN_URL", "https://your-naumen-server.com")
NAUMEN_API_KEY = os.getenv("NAUMEN_API_KEY", "your-api-key-here")
NAUMEN_VERIFY_SSL = os.getenv("NAUMEN_VERIFY_SSL", "true").lower() == "true"

# ===========================
# AI/ML настройки
# ===========================
AUTO_APPLY_THRESHOLD = float(os.getenv("AUTO_APPLY_THRESHOLD", "0.80"))
MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.50"))

# Категории для классификации
CATEGORIES = [
    "Почта",
    "Сеть",
    "1C",
    "Оборудование",
    "Доступ",
    "Прочее"
]

# Приоритеты
PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

# Группы поддержки
SUPPORT_GROUPS = {
    "Почта": "email-support-team",
    "Сеть": "network-support-team",
    "1C": "1c-support-team",
    "Оборудование": "hardware-support-team",
    "Доступ": "access-support-team",
    "Прочее": "general-support-team"
}

# Маппинг категорий на группы поддержки
CATEGORY_TO_GROUP_MAPPING = SUPPORT_GROUPS

# ===========================
# Logging настройки
# ===========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / os.getenv("LOG_FILE", "ai_assistant.log")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

# ===========================
# Metrics настройки
# ===========================
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))

# ===========================
# Режим работы
# ===========================
# DRY_RUN_MODE - если True, только логирование без изменения тикетов
DRY_RUN_MODE = os.getenv("DRY_RUN_MODE", "false").lower() == "true"

# ===========================
# Webhook настройки
# ===========================
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# ===========================
# Валидация конфигурации
# ===========================
def validate_config():
    """Проверка обязательных настроек"""
    errors = []

    # Проверяем критичные настройки только если не в DRY_RUN режиме
    if not DRY_RUN_MODE:
        if NAUMEN_URL == "https://your-naumen-server.com":
            errors.append("NAUMEN_URL не настроен")
        if NAUMEN_API_KEY == "your-api-key-here":
            errors.append("NAUMEN_API_KEY не настроен")

    # Проверяем пороговые значения
    if not (0 <= AUTO_APPLY_THRESHOLD <= 1):
        errors.append(f"AUTO_APPLY_THRESHOLD должен быть между 0 и 1, получено: {AUTO_APPLY_THRESHOLD}")
    if not (0 <= MIN_CONFIDENCE_THRESHOLD <= 1):
        errors.append(f"MIN_CONFIDENCE_THRESHOLD должен быть между 0 и 1, получено: {MIN_CONFIDENCE_THRESHOLD}")

    if errors:
        print("⚠️  ПРЕДУПРЕЖДЕНИЯ КОНФИГУРАЦИИ:")
        for error in errors:
            print(f"   - {error}")
        if not DRY_RUN_MODE:
            print("\n❗ Для продакшн использования исправьте настройки в .env файле")
        print()

    return len(errors) == 0

# Автоматическая проверка при импорте
if __name__ != "__main__":
    validate_config()
