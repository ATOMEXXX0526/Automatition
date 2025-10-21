"""
Мониторинг SLA и автоматические напоминания
Автоматизация контроля соблюдения SLA в Naumen Service Desk
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from naumen_sdk import NaumenClient
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SLAMonitor:
    """Монитор SLA для заявок"""

    def __init__(self, client: NaumenClient):
        self.client = client
        self.sla_rules = {
            "critical": {"response": 1, "resolution": 4},  # часы
            "high": {"response": 2, "resolution": 8},
            "normal": {"response": 4, "resolution": 24},
            "low": {"response": 8, "resolution": 72}
        }

    def calculate_sla_breach(self, service_call: Dict) -> Dict:
        """
        Рассчитать нарушение SLA для заявки

        Args:
            service_call: Данные заявки

        Returns:
            Информация о нарушении SLA
        """
        priority = service_call.get('priority', 'normal')
        created_at = datetime.fromisoformat(service_call.get('createdAt', ''))
        now = datetime.now()
        time_elapsed = (now - created_at).total_seconds() / 3600  # часы

        sla_limits = self.sla_rules.get(priority, self.sla_rules['normal'])

        breach_info = {
            'uuid': service_call['uuid'],
            'priority': priority,
            'time_elapsed': time_elapsed,
            'response_sla': sla_limits['response'],
            'resolution_sla': sla_limits['resolution'],
            'response_breached': False,
            'resolution_breached': False,
            'time_to_breach': None
        }

        # Проверка нарушения SLA на ответ
        if not service_call.get('first_response_at'):
            if time_elapsed > sla_limits['response']:
                breach_info['response_breached'] = True
            else:
                breach_info['time_to_breach'] = sla_limits['response'] - time_elapsed

        # Проверка нарушения SLA на решение
        if service_call.get('status') not in ['closed', 'resolved']:
            if time_elapsed > sla_limits['resolution']:
                breach_info['resolution_breached'] = True
            else:
                breach_info['time_to_breach'] = min(
                    breach_info.get('time_to_breach', float('inf')),
                    sla_limits['resolution'] - time_elapsed
                )

        return breach_info

    def check_sla_breaches(self, filters: Dict = None) -> List[Dict]:
        """
        Проверить заявки на нарушения SLA

        Args:
            filters: Фильтры для поиска заявок

        Returns:
            Список заявок с нарушениями SLA
        """
        if filters is None:
            filters = {"status": ["new", "in_progress", "assigned"]}

        service_calls = self.client.search_service_calls(filters)
        breaches = []

        for sc in service_calls:
            breach_info = self.calculate_sla_breach(sc)
            if breach_info['response_breached'] or breach_info['resolution_breached']:
                breaches.append(breach_info)
                logger.warning(f"SLA breach detected for {sc['uuid']}")

        return breaches

    def send_sla_warnings(self, warning_threshold: float = 0.8) -> List[Dict]:
        """
        Отправить предупреждения о приближении к нарушению SLA

        Args:
            warning_threshold: Порог предупреждения (0.8 = 80% от времени SLA)

        Returns:
            Список заявок с отправленными предупреждениями
        """
        filters = {"status": ["new", "in_progress", "assigned"]}
        service_calls = self.client.search_service_calls(filters)
        warnings_sent = []

        for sc in service_calls:
            breach_info = self.calculate_sla_breach(sc)

            if breach_info['time_to_breach'] is not None:
                sla_limit = breach_info['resolution_sla']
                time_used = breach_info['time_elapsed']

                if (time_used / sla_limit) >= warning_threshold:
                    # Отправка предупреждения
                    warning_msg = (
                        f"⚠️ Внимание! До нарушения SLA осталось "
                        f"{breach_info['time_to_breach']:.1f} часов. "
                        f"Приоритет: {breach_info['priority']}"
                    )

                    self.client.add_comment(sc['uuid'], warning_msg, is_private=True)
                    warnings_sent.append(breach_info)
                    logger.info(f"SLA warning sent for {sc['uuid']}")

        return warnings_sent

    def auto_escalate_breaches(self) -> List[Dict]:
        """
        Автоматически эскалировать заявки с нарушением SLA

        Returns:
            Список эскалированных заявок
        """
        breaches = self.check_sla_breaches()
        escalated = []

        for breach in breaches:
            try:
                # Повышение приоритета
                current_priority = breach['priority']
                new_priority = self._escalate_priority(current_priority)

                self.client.update_service_call(
                    breach['uuid'],
                    priority=new_priority,
                    escalated=True
                )

                # Добавление комментария
                comment = (
                    f"🔴 Автоматическая эскалация из-за нарушения SLA!\n"
                    f"Прошло времени: {breach['time_elapsed']:.1f} ч\n"
                    f"SLA: {breach['resolution_sla']} ч\n"
                    f"Приоритет изменен: {current_priority} → {new_priority}"
                )
                self.client.add_comment(breach['uuid'], comment)

                escalated.append(breach)
                logger.info(f"Auto-escalated {breach['uuid']}")

            except Exception as e:
                logger.error(f"Failed to escalate {breach['uuid']}: {e}")

        return escalated

    def _escalate_priority(self, current: str) -> str:
        """Повысить приоритет"""
        priority_map = {
            "low": "normal",
            "normal": "high",
            "high": "critical",
            "critical": "critical"
        }
        return priority_map.get(current, "high")

    def generate_sla_report(self, start_date: datetime = None,
                          end_date: datetime = None) -> Dict:
        """
        Сгенерировать отчет по SLA

        Args:
            start_date: Начало периода
            end_date: Конец периода

        Returns:
            Отчет с метриками SLA
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()

        filters = {
            "createdAt": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            }
        }

        service_calls = self.client.search_service_calls(filters)

        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_calls": len(service_calls),
            "sla_met": 0,
            "sla_breached": 0,
            "by_priority": {},
            "average_response_time": 0,
            "average_resolution_time": 0
        }

        for sc in service_calls:
            breach_info = self.calculate_sla_breach(sc)
            priority = breach_info['priority']

            if priority not in report['by_priority']:
                report['by_priority'][priority] = {
                    "total": 0,
                    "met": 0,
                    "breached": 0
                }

            report['by_priority'][priority]['total'] += 1

            if breach_info['response_breached'] or breach_info['resolution_breached']:
                report['sla_breached'] += 1
                report['by_priority'][priority]['breached'] += 1
            else:
                report['sla_met'] += 1
                report['by_priority'][priority]['met'] += 1

        if report['total_calls'] > 0:
            report['sla_compliance_rate'] = (
                report['sla_met'] / report['total_calls'] * 100
            )

        return report


if __name__ == "__main__":
    # Пример использования
    from config import NAUMEN_URL, NAUMEN_API_KEY

    client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)
    sla_monitor = SLAMonitor(client)

    # Проверка нарушений SLA
    breaches = sla_monitor.check_sla_breaches()
    print(f"Found {len(breaches)} SLA breaches")

    # Отправка предупреждений
    warnings = sla_monitor.send_sla_warnings(warning_threshold=0.8)
    print(f"Sent {len(warnings)} SLA warnings")

    # Генерация отчета
    report = sla_monitor.generate_sla_report()
    print(f"SLA compliance rate: {report.get('sla_compliance_rate', 0):.2f}%")
