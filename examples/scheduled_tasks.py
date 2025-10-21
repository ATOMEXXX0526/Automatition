"""
Примеры планируемых задач для автоматизации
Можно запускать через cron или другой планировщик
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from naumen_sdk import NaumenClient
from automation.sla_monitor import SLAMonitor
from automation.auto_incident_handler import IncidentHandler
from config import NAUMEN_URL, NAUMEN_API_KEY, SLA_WARNING_THRESHOLD
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduled_tasks.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def task_check_sla():
    """
    Задача: Проверка SLA и отправка предупреждений
    Рекомендуется запускать каждые 15-30 минут
    """
    logger.info("Starting SLA check task")

    try:
        client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)
        sla_monitor = SLAMonitor(client)

        # Проверка нарушений
        breaches = sla_monitor.check_sla_breaches()
        logger.info(f"Found {len(breaches)} SLA breaches")

        # Отправка предупреждений
        warnings = sla_monitor.send_sla_warnings(SLA_WARNING_THRESHOLD)
        logger.info(f"Sent {len(warnings)} SLA warnings")

        # Автоэскалация нарушений
        escalated = sla_monitor.auto_escalate_breaches()
        logger.info(f"Auto-escalated {len(escalated)} service calls")

        return {
            "success": True,
            "breaches": len(breaches),
            "warnings": len(warnings),
            "escalated": len(escalated)
        }

    except Exception as e:
        logger.error(f"SLA check task failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def task_escalate_old_incidents():
    """
    Задача: Эскалация старых инцидентов
    Рекомендуется запускать каждый час
    """
    logger.info("Starting old incidents escalation task")

    try:
        client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)
        incident_handler = IncidentHandler(client)

        filters = {
            "status": ["new", "in_progress", "assigned"]
        }

        escalated = incident_handler.monitor_and_escalate(
            filters,
            escalation_hours=24
        )

        logger.info(f"Escalated {len(escalated)} old incidents")

        return {
            "success": True,
            "escalated": len(escalated)
        }

    except Exception as e:
        logger.error(f"Old incidents escalation task failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def task_daily_sla_report():
    """
    Задача: Генерация ежедневного отчета по SLA
    Рекомендуется запускать раз в день (например, в 9:00)
    """
    logger.info("Starting daily SLA report generation")

    try:
        client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)
        sla_monitor = SLAMonitor(client)

        report = sla_monitor.generate_sla_report()

        logger.info("Daily SLA Report:")
        logger.info(f"  Total calls: {report['total_calls']}")
        logger.info(f"  SLA met: {report['sla_met']}")
        logger.info(f"  SLA breached: {report['sla_breached']}")
        logger.info(f"  Compliance rate: {report.get('sla_compliance_rate', 0):.2f}%")

        # Здесь можно добавить отправку отчета по email
        # send_email_report(report)

        return {
            "success": True,
            "report": report
        }

    except Exception as e:
        logger.error(f"Daily SLA report task failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def task_cleanup_test_data():
    """
    Задача: Очистка тестовых данных
    Рекомендуется запускать раз в неделю
    """
    logger.info("Starting test data cleanup task")

    try:
        client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)

        # Поиск тестовых заявок (начинаются с [TEST] или [ТЕСТ])
        test_filters = {
            "title": {"contains": ["[TEST]", "[ТЕСТ]"]},
            "status": ["closed"]
        }

        test_calls = client.search_service_calls(test_filters)

        logger.info(f"Found {len(test_calls)} test service calls for cleanup")

        # Здесь можно добавить логику удаления или архивации
        # Обычно в Naumen нельзя удалять заявки, только архивировать

        return {
            "success": True,
            "found": len(test_calls)
        }

    except Exception as e:
        logger.error(f"Cleanup task failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def task_monitor_unassigned():
    """
    Задача: Мониторинг неназначенных заявок
    Рекомендуется запускать каждые 30 минут
    """
    logger.info("Starting unassigned service calls monitoring")

    try:
        client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)

        # Поиск неназначенных заявок старше 2 часов
        filters = {
            "assignee": None,
            "status": ["new", "registered"]
        }

        unassigned = client.search_service_calls(filters)

        logger.info(f"Found {len(unassigned)} unassigned service calls")

        # Добавление комментариев к старым неназначенным заявкам
        for call in unassigned:
            created_at = datetime.fromisoformat(call.get('createdAt', ''))
            hours_open = (datetime.now() - created_at).total_seconds() / 3600

            if hours_open > 2:
                client.add_comment(
                    call['uuid'],
                    f"⚠️ Внимание! Заявка не назначена уже {hours_open:.1f} часов. Требуется назначение ответственного.",
                    is_private=True
                )
                logger.warning(f"Added warning comment to {call['uuid']}")

        return {
            "success": True,
            "unassigned": len(unassigned)
        }

    except Exception as e:
        logger.error(f"Unassigned monitoring task failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    """
    Запуск задач вручную для тестирования

    В production используйте cron:

    # Проверка SLA каждые 15 минут
    */15 * * * * /usr/bin/python3 /path/to/scheduled_tasks.py sla_check

    # Эскалация старых инцидентов каждый час
    0 * * * * /usr/bin/python3 /path/to/scheduled_tasks.py escalate_old

    # Ежедневный отчет в 9:00
    0 9 * * * /usr/bin/python3 /path/to/scheduled_tasks.py daily_report

    # Очистка тестовых данных каждое воскресенье в 23:00
    0 23 * * 0 /usr/bin/python3 /path/to/scheduled_tasks.py cleanup

    # Мониторинг неназначенных каждые 30 минут
    */30 * * * * /usr/bin/python3 /path/to/scheduled_tasks.py monitor_unassigned
    """

    import sys

    tasks = {
        "sla_check": task_check_sla,
        "escalate_old": task_escalate_old_incidents,
        "daily_report": task_daily_sla_report,
        "cleanup": task_cleanup_test_data,
        "monitor_unassigned": task_monitor_unassigned,
    }

    if len(sys.argv) > 1:
        task_name = sys.argv[1]
        if task_name in tasks:
            logger.info(f"Running task: {task_name}")
            result = tasks[task_name]()
            logger.info(f"Task result: {result}")
        else:
            print(f"Unknown task: {task_name}")
            print(f"Available tasks: {', '.join(tasks.keys())}")
    else:
        # Запуск всех задач для тестирования
        logger.info("Running all tasks for testing")
        for task_name, task_func in tasks.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Running: {task_name}")
            logger.info(f"{'='*60}")
            result = task_func()
            logger.info(f"Result: {result}")
