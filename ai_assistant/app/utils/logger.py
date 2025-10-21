"""
Система логирования для AI Assistant (упрощенная версия)
"""
import logging
import sys
import json
from pathlib import Path
from ai_assistant.app.config import LOG_LEVEL, LOG_FILE, LOG_FORMAT


class JSONFormatter(logging.Formatter):
    """Простой JSON форматтер"""

    def format(self, record):
        log_data = {
            'asctime': self.formatTime(record, '%Y-%m-%d %H:%M:%S'),
            'name': record.name,
            'levelname': record.levelname,
            'message': record.getMessage()
        }

        # Добавляем extra поля если есть
        if hasattr(record, 'event'):
            log_data['event'] = record.event
        if hasattr(record, 'ticket_id'):
            log_data['ticket_id'] = record.ticket_id
        if hasattr(record, 'category'):
            log_data['category'] = record.category
        if hasattr(record, 'confidence'):
            log_data['confidence'] = record.confidence
        if hasattr(record, 'processing_time_ms'):
            log_data['processing_time_ms'] = record.processing_time_ms
        if hasattr(record, 'auto_applied'):
            log_data['auto_applied'] = record.auto_applied
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type
        if hasattr(record, 'error_message'):
            log_data['error_message'] = record.error_message

        return json.dumps(log_data, ensure_ascii=False)


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
        json_formatter = JSONFormatter()
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
