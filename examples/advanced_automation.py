"""
Продвинутые примеры автоматизации для Naumen Service Desk
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from naumen_sdk import NaumenClient
from automation.auto_incident_handler import IncidentHandler
from automation.bulk_operations import BulkOperations, TemplateProcessor
from automation.sla_monitor import SLAMonitor
from config import NAUMEN_URL, NAUMEN_API_KEY, TEAM_MAPPING

# Инициализация
client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)

# ========== Пример 1: Автоматическая классификация инцидентов ==========
print("=" * 70)
print("Пример 1: Автоматическая классификация и создание инцидента")
print("=" * 70)

incident_handler = IncidentHandler(client)

# Создание инцидента с автоматическим определением приоритета
incident = incident_handler.create_smart_incident(
    title="Критическая ошибка в 1C: зависание при проведении документов",
    description="При попытке провести документ реализации система 1C зависает. Работа бухгалтерии заблокирована.",
    client_uuid="client-uuid-here",
    team_mapping=TEAM_MAPPING
)

print(f"✓ Создан инцидент: {incident.get('uuid')}")
print(f"  Автоматически определен приоритет: {incident.get('urgency')}")
print(f"  Назначена команда на основе ключевых слов")
print()

# ========== Пример 2: Массовое обновление заявок ==========
print("=" * 70)
print("Пример 2: Массовое обновление заявок")
print("=" * 70)

bulk_ops = BulkOperations(client, max_workers=5)

# Поиск всех заявок со статусом "new" и низким приоритетом
search_filters = {
    "status": "new",
    "priority": "low"
}

# Массовое обновление: повышаем приоритет старых заявок
results = bulk_ops.search_and_process(
    search_filters,
    lambda uuid: client.update_service_call(uuid, priority="normal")
)

print(f"✓ Обновлено заявок: {len(results)}")
print(f"  Успешно: {sum(1 for r in results.values() if 'error' not in r)}")
print(f"  Ошибок: {sum(1 for r in results.values() if 'error' in r)}")
print()

# ========== Пример 3: Массовое добавление комментариев ==========
print("=" * 70)
print("Пример 3: Массовое добавление комментариев")
print("=" * 70)

# Получаем список UUID заявок для обработки
service_call_uuids = ["uuid1", "uuid2", "uuid3"]  # Замените на реальные UUID

results = bulk_ops.bulk_comment(
    service_call_uuids,
    "Напоминание: пожалуйста, предоставьте дополнительную информацию по заявке.",
    is_private=False,
    delay=0.5
)

print(f"✓ Комментарии добавлены к {len(results)} заявкам")
print()

# ========== Пример 4: Создание заявок по шаблону ==========
print("=" * 70)
print("Пример 4: Создание заявок по шаблону")
print("=" * 70)

template_processor = TemplateProcessor(client)

# Шаблон для создания заявок на обслуживание
template = {
    "title": "Плановое обслуживание {equipment} в {location}",
    "description": "Требуется провести плановое техническое обслуживание {equipment}, расположенного в {location}. Дата: {date}.",
    "client_uuid": "default-client-uuid",
    "priority": "normal"
}

# Данные для подстановки
equipment_list = [
    {"equipment": "Сервер Dell R740", "location": "Серверная А", "date": "2025-11-01"},
    {"equipment": "Принтер HP LaserJet", "location": "Офис 305", "date": "2025-11-02"},
    {"equipment": "ИБП APC", "location": "Серверная Б", "date": "2025-11-03"},
]

created_calls = template_processor.create_from_template(template, equipment_list)

print(f"✓ Создано заявок по шаблону: {len(created_calls)}")
for call in created_calls:
    print(f"  - {call.get('title')} (#{call.get('number')})")
print()

# ========== Пример 5: Мониторинг SLA ==========
print("=" * 70)
print("Пример 5: Мониторинг SLA и автоматическая эскалация")
print("=" * 70)

sla_monitor = SLAMonitor(client)

# Проверка нарушений SLA
breaches = sla_monitor.check_sla_breaches()

print(f"✓ Найдено нарушений SLA: {len(breaches)}")

if breaches:
    print("  Нарушения:")
    for breach in breaches[:5]:  # Показываем первые 5
        print(f"    - Заявка {breach['uuid']}")
        print(f"      Приоритет: {breach['priority']}")
        print(f"      Прошло времени: {breach['time_elapsed']:.1f} ч")
        print(f"      SLA: {breach['resolution_sla']} ч")
        print()

# Отправка предупреждений о приближении к нарушению SLA
warnings = sla_monitor.send_sla_warnings(warning_threshold=0.8)

print(f"✓ Отправлено предупреждений о приближении к SLA: {len(warnings)}")
print()

# Автоматическая эскалация нарушений
escalated = sla_monitor.auto_escalate_breaches()

print(f"✓ Автоматически эскалировано заявок: {len(escalated)}")
print()

# ========== Пример 6: Генерация отчета по SLA ==========
print("=" * 70)
print("Пример 6: Генерация отчета по SLA за последний месяц")
print("=" * 70)

report = sla_monitor.generate_sla_report()

print(f"✓ Отчет по SLA:")
print(f"  Период: {report['period']['start']} - {report['period']['end']}")
print(f"  Всего заявок: {report['total_calls']}")
print(f"  SLA соблюден: {report['sla_met']}")
print(f"  SLA нарушен: {report['sla_breached']}")
print(f"  Уровень соблюдения SLA: {report.get('sla_compliance_rate', 0):.2f}%")
print()
print("  По приоритетам:")
for priority, stats in report.get('by_priority', {}).items():
    print(f"    {priority}: {stats['met']}/{stats['total']} "
          f"({stats['met']/stats['total']*100:.1f}% соблюдено)")
print()

# ========== Пример 7: Мониторинг и эскалация старых инцидентов ==========
print("=" * 70)
print("Пример 7: Мониторинг и эскалация инцидентов старше 24 часов")
print("=" * 70)

# Поиск открытых инцидентов
open_incidents_filters = {
    "status": ["new", "in_progress"],
}

escalated_incidents = incident_handler.monitor_and_escalate(
    open_incidents_filters,
    escalation_hours=24
)

print(f"✓ Эскалировано инцидентов (открыто >24ч): {len(escalated_incidents)}")
print()

print("=" * 70)
print("Все примеры автоматизации выполнены!")
print("=" * 70)
