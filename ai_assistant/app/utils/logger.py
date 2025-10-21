"""
Система логирования для AI Assistant
"""
import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger
from app.config import LOG_LEVEL, LOG_FILE, LOG_FORMAT


def setup_logger(name: str = "ai_assistant") -> logging.Logger:
    """
    Настройка логгера с поддержкой JSON формата

    Args:
        name: Имя логгера

    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Удаляем существующие handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(getattr(logging, LOG_LEVEL))

    # Форматтеры
    if LOG_FORMAT == "json":
        # JSON формат для машинной обработки
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            timestamp=True
        )
        console_handler.setFormatter(json_formatter)
        file_handler.setFormatter(json_formatter)
    else:
        # Текстовый формат для читаемости
        text_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(text_formatter)
        file_handler.setFormatter(text_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Создаем глобальный логгер
logger = setup_logger()


def log_classification(ticket_id: str, subject: str, prediction: dict, confidence: float,
                       processing_time: float, auto_applied: bool = False):
    """
    Логирование классификации заявки

    Args:
        ticket_id: ID заявки
        subject: Тема заявки
        prediction: Результат классификации
        confidence: Уверенность модели
        processing_time: Время обработки (сек)
        auto_applied: Было ли автоприменение
    """
    logger.info(
        "Classification completed",
        extra={
            "event": "classification",
            "ticket_id": ticket_id,
            "subject": subject,
            "category": prediction.get("category"),
            "support_group": prediction.get("support_group"),
            "priority": prediction.get("priority"),
            "confidence": confidence,
            "processing_time_ms": round(processing_time * 1000, 2),
            "auto_applied": auto_applied
        }
    )


def log_error(ticket_id: str, error_message: str, error_type: str = "unknown"):
    """
    Логирование ошибки

    Args:
        ticket_id: ID заявки
        error_message: Сообщение об ошибке
        error_type: Тип ошибки
    """
    logger.error(
        "Error occurred",
        extra={
            "event": "error",
            "ticket_id": ticket_id,
            "error_type": error_type,
            "error_message": error_message
        },
        exc_info=True
    )
