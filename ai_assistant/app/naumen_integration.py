"""
Интеграция с Naumen Service Desk API
"""
import sys
from pathlib import Path

# Добавляем родительскую директорию в PYTHONPATH для импорта naumen_sdk
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from naumen_sdk import NaumenClient
from app.config import NAUMEN_URL, NAUMEN_API_KEY, NAUMEN_VERIFY_SSL, DRY_RUN_MODE
from app.utils.logger import logger
from typing import Dict, Optional


class NaumenIntegration:
    """
    Класс для интеграции с Naumen Service Desk
    """

    def __init__(self):
        """Инициализация клиента Naumen"""
        self.client = None
        if NAUMEN_API_KEY and NAUMEN_URL:
            try:
                self.client = NaumenClient(
                    base_url=NAUMEN_URL,
                    access_key=NAUMEN_API_KEY,
                    verify_ssl=NAUMEN_VERIFY_SSL
                )
                logger.info(f"Naumen client initialized: {NAUMEN_URL}")
            except Exception as e:
                logger.error(f"Failed to initialize Naumen client: {e}")
                self.client = None
        else:
            logger.warning("Naumen credentials not provided. Running in standalone mode.")

    def update_ticket(self, ticket_id: str, classification: Dict) -> bool:
        """
        Обновление заявки в Naumen с результатами классификации

        Args:
            ticket_id: ID заявки
            classification: Результат классификации

        Returns:
            True если успешно, False иначе
        """
        if DRY_RUN_MODE:
            logger.info(
                f"DRY RUN: Would update ticket {ticket_id} with classification: {classification}"
            )
            return True

        if not self.client:
            logger.error("Naumen client not initialized")
            return False

        try:
            # Обновляем заявку
            update_data = {
                "category": classification.get("category"),
                "priority": classification.get("priority"),
                # support_group может требовать UUID, а не название
                # Здесь нужно добавить маппинг названия группы в UUID
            }

            self.client.update_service_call(ticket_id, **update_data)

            # Добавляем комментарий о классификации
            comment_text = (
                f"Автоматическая классификация:\n"
                f"Категория: {classification.get('category')}\n"
                f"Группа поддержки: {classification.get('support_group')}\n"
                f"Приоритет: {classification.get('priority')}\n"
                f"Уверенность: {classification.get('confidence'):.2%}\n"
                f"Метод: {classification.get('method', 'unknown')}"
            )

            self.client.add_comment(
                ticket_id,
                comment_text,
                is_private=True  # Внутренний комментарий
            )

            logger.info(f"Successfully updated ticket {ticket_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update ticket {ticket_id}: {e}")
            return False

    def add_suggestion_comment(self, ticket_id: str, classification: Dict) -> bool:
        """
        Добавление комментария с рекомендацией (не применяя изменения)

        Args:
            ticket_id: ID заявки
            classification: Результат классификации

        Returns:
            True если успешно, False иначе
        """
        if DRY_RUN_MODE:
            logger.info(
                f"DRY RUN: Would add suggestion to ticket {ticket_id}: {classification}"
            )
            return True

        if not self.client:
            logger.error("Naumen client not initialized")
            return False

        try:
            comment_text = (
                f"🤖 Рекомендация AI Assistant:\n\n"
                f"Категория: {classification.get('category')}\n"
                f"Группа поддержки: {classification.get('support_group')}\n"
                f"Приоритет: {classification.get('priority')}\n"
                f"Уверенность: {classification.get('confidence'):.2%}\n\n"
                f"Рекомендуется применить эту классификацию вручную."
            )

            self.client.add_comment(
                ticket_id,
                comment_text,
                is_private=True
            )

            logger.info(f"Added suggestion comment to ticket {ticket_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add suggestion to ticket {ticket_id}: {e}")
            return False

    def get_ticket_info(self, ticket_id: str) -> Optional[Dict]:
        """
        Получение информации о заявке

        Args:
            ticket_id: ID заявки

        Returns:
            Словарь с информацией о заявке или None
        """
        if not self.client:
            logger.error("Naumen client not initialized")
            return None

        try:
            ticket = self.client.get_service_call(ticket_id)
            logger.info(f"Retrieved ticket info for {ticket_id}")
            return ticket
        except Exception as e:
            logger.error(f"Failed to get ticket {ticket_id}: {e}")
            return None


# Singleton instance
_integration_instance = None


def get_naumen_integration() -> NaumenIntegration:
    """
    Получить экземпляр интеграции с Naumen (singleton)

    Returns:
        NaumenIntegration
    """
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = NaumenIntegration()
    return _integration_instance
