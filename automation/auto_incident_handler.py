"""
Автоматический обработчик инцидентов
Автоматизация для обработки и классификации инцидентов в Naumen Service Desk
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from naumen_sdk import NaumenClient
from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IncidentHandler:
    """Автоматический обработчик инцидентов"""

    def __init__(self, client: NaumenClient):
        self.client = client
        self.priority_keywords = {
            "critical": ["критический", "авария", "система упала", "не работает сайт"],
            "high": ["срочно", "блокирующая", "не могу работать"],
            "normal": ["проблема", "ошибка", "issue"],
            "low": ["вопрос", "консультация", "рекомендация"]
        }

    def auto_classify_priority(self, title: str, description: str) -> str:
        """
        Автоматически определить приоритет инцидента на основе ключевых слов

        Args:
            title: Заголовок инцидента
            description: Описание инцидента

        Returns:
            Приоритет: critical, high, normal или low
        """
        text = f"{title} {description}".lower()

        for priority, keywords in self.priority_keywords.items():
            if any(keyword in text for keyword in keywords):
                logger.info(f"Auto-classified priority as: {priority}")
                return priority

        return "normal"

    def auto_assign_by_keywords(self, title: str, description: str,
                                team_mapping: Dict[str, str]) -> str:
        """
        Автоматически назначить команду на основе ключевых слов

        Args:
            title: Заголовок инцидента
            description: Описание инцидента
            team_mapping: Словарь {keyword: team_uuid}

        Returns:
            UUID команды
        """
        text = f"{title} {description}".lower()

        for keyword, team_uuid in team_mapping.items():
            if keyword.lower() in text:
                logger.info(f"Auto-assigned to team: {team_uuid} (keyword: {keyword})")
                return team_uuid

        return None

    def create_smart_incident(self,
                            title: str,
                            description: str,
                            client_uuid: str,
                            team_mapping: Dict[str, str] = None,
                            **kwargs) -> Dict:
        """
        Создать инцидент с автоматической классификацией

        Args:
            title: Заголовок
            description: Описание
            client_uuid: UUID клиента
            team_mapping: Маппинг ключевых слов на команды
            **kwargs: Дополнительные параметры

        Returns:
            Созданный инцидент
        """
        # Автоопределение приоритета
        priority = self.auto_classify_priority(title, description)

        incident_data = {
            "title": title,
            "description": description,
            "client": client_uuid,
            "urgency": priority,
            "impact": priority,
            **kwargs
        }

        # Автоназначение команды
        if team_mapping:
            team_uuid = self.auto_assign_by_keywords(title, description, team_mapping)
            if team_uuid:
                incident_data["responsible_team"] = team_uuid

        return self.client.create_incident(**incident_data)

    def monitor_and_escalate(self, filters: Dict, escalation_hours: int = 24) -> List[Dict]:
        """
        Мониторинг инцидентов и автоматическая эскалация

        Args:
            filters: Фильтры для поиска инцидентов
            escalation_hours: Часов до эскалации

        Returns:
            Список эскалированных инцидентов
        """
        incidents = self.client.search_service_calls(filters)
        escalated = []

        for incident in incidents:
            # Проверка времени создания
            created_at = datetime.fromisoformat(incident.get('createdAt', ''))
            hours_open = (datetime.now() - created_at).total_seconds() / 3600

            if hours_open > escalation_hours:
                # Эскалация
                self.client.update_service_call(
                    incident['uuid'],
                    urgency='high',
                    escalated=True
                )
                self.client.add_comment(
                    incident['uuid'],
                    f"Автоматическая эскалация: инцидент открыт более {escalation_hours} часов"
                )
                escalated.append(incident)
                logger.info(f"Escalated incident: {incident['uuid']}")

        return escalated


if __name__ == "__main__":
    # Пример использования
    from config import NAUMEN_URL, NAUMEN_API_KEY

    client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)
    handler = IncidentHandler(client)

    # Создание инцидента с автоклассификацией
    team_mapping = {
        "сеть": "team-uuid-network",
        "1c": "team-uuid-1c",
        "почта": "team-uuid-email",
    }

    incident = handler.create_smart_incident(
        title="Критическая проблема с сетью",
        description="Не работает доступ к интернету во всем офисе",
        client_uuid="client-uuid-here",
        team_mapping=team_mapping
    )

    print(f"Created incident: {incident['uuid']}")
