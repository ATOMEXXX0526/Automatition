"""
Массовые операции с заявками
Автоматизация для выполнения массовых действий над заявками
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from naumen_sdk import NaumenClient
from typing import List, Dict, Callable
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)


class BulkOperations:
    """Класс для массовых операций с заявками"""

    def __init__(self, client: NaumenClient, max_workers: int = 5):
        """
        Args:
            client: Naumen клиент
            max_workers: Максимальное количество параллельных потоков
        """
        self.client = client
        self.max_workers = max_workers

    def bulk_update(self, uuids: List[str], update_data: Dict,
                   delay: float = 0.5) -> Dict[str, any]:
        """
        Массовое обновление заявок

        Args:
            uuids: Список UUID заявок
            update_data: Данные для обновления
            delay: Задержка между запросами (секунды)

        Returns:
            Словарь с результатами {uuid: result/error}
        """
        results = {}

        for uuid in uuids:
            try:
                result = self.client.update_service_call(uuid, **update_data)
                results[uuid] = result
                logger.info(f"Updated {uuid}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Failed to update {uuid}: {e}")
                results[uuid] = {"error": str(e)}

        return results

    def bulk_close(self, uuids: List[str], resolution: str,
                  delay: float = 0.5) -> Dict[str, any]:
        """
        Массовое закрытие заявок

        Args:
            uuids: Список UUID заявок
            resolution: Комментарий при закрытии
            delay: Задержка между запросами

        Returns:
            Словарь с результатами
        """
        results = {}

        for uuid in uuids:
            try:
                result = self.client.close_service_call(uuid, resolution)
                results[uuid] = result
                logger.info(f"Closed {uuid}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Failed to close {uuid}: {e}")
                results[uuid] = {"error": str(e)}

        return results

    def bulk_comment(self, uuids: List[str], comment: str,
                    is_private: bool = False, delay: float = 0.5) -> Dict[str, any]:
        """
        Массовое добавление комментариев

        Args:
            uuids: Список UUID заявок
            comment: Текст комментария
            is_private: Приватный комментарий
            delay: Задержка между запросами

        Returns:
            Словарь с результатами
        """
        results = {}

        for uuid in uuids:
            try:
                result = self.client.add_comment(uuid, comment, is_private)
                results[uuid] = result
                logger.info(f"Added comment to {uuid}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Failed to add comment to {uuid}: {e}")
                results[uuid] = {"error": str(e)}

        return results

    def bulk_assign(self, uuids: List[str], assignee_uuid: str,
                   delay: float = 0.5) -> Dict[str, any]:
        """
        Массовое назначение ответственного

        Args:
            uuids: Список UUID заявок
            assignee_uuid: UUID ответственного
            delay: Задержка между запросами

        Returns:
            Словарь с результатами
        """
        return self.bulk_update(uuids, {"assignee": assignee_uuid}, delay)

    def parallel_bulk_operation(self, uuids: List[str],
                               operation: Callable,
                               *args, **kwargs) -> Dict[str, any]:
        """
        Параллельное выполнение операции над списком заявок

        Args:
            uuids: Список UUID заявок
            operation: Функция операции (принимает uuid как первый аргумент)
            *args, **kwargs: Аргументы для операции

        Returns:
            Словарь с результатами
        """
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_uuid = {
                executor.submit(operation, uuid, *args, **kwargs): uuid
                for uuid in uuids
            }

            for future in as_completed(future_to_uuid):
                uuid = future_to_uuid[future]
                try:
                    result = future.result()
                    results[uuid] = result
                    logger.info(f"Completed operation for {uuid}")
                except Exception as e:
                    logger.error(f"Operation failed for {uuid}: {e}")
                    results[uuid] = {"error": str(e)}

        return results

    def search_and_process(self, search_filters: Dict,
                          operation: Callable,
                          *args, **kwargs) -> Dict[str, any]:
        """
        Поиск заявок и выполнение операции над найденными

        Args:
            search_filters: Фильтры для поиска
            operation: Операция для выполнения
            *args, **kwargs: Аргументы операции

        Returns:
            Словарь с результатами
        """
        # Поиск заявок
        service_calls = self.client.search_service_calls(search_filters)
        uuids = [sc['uuid'] for sc in service_calls]

        logger.info(f"Found {len(uuids)} service calls matching filters")

        # Выполнение операции
        return self.parallel_bulk_operation(uuids, operation, *args, **kwargs)


class TemplateProcessor:
    """Обработчик шаблонов для массового создания заявок"""

    def __init__(self, client: NaumenClient):
        self.client = client

    def create_from_template(self, template: Dict,
                           variables: List[Dict]) -> List[Dict]:
        """
        Создание заявок по шаблону с переменными

        Args:
            template: Шаблон заявки
            variables: Список словарей с переменными для подстановки

        Returns:
            Список созданных заявок
        """
        created = []

        for var_set in variables:
            # Подстановка переменных в шаблон
            service_call_data = {}
            for key, value in template.items():
                if isinstance(value, str):
                    service_call_data[key] = value.format(**var_set)
                else:
                    service_call_data[key] = value

            # Создание заявки
            try:
                result = self.client.create_service_call(**service_call_data)
                created.append(result)
                logger.info(f"Created service call from template: {result['uuid']}")
            except Exception as e:
                logger.error(f"Failed to create service call: {e}")

        return created


if __name__ == "__main__":
    # Пример использования
    from config import NAUMEN_URL, NAUMEN_API_KEY

    client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)
    bulk_ops = BulkOperations(client)

    # Пример массового обновления
    uuids = ["uuid1", "uuid2", "uuid3"]
    results = bulk_ops.bulk_update(uuids, {"priority": "high"})
    print(f"Updated {len(results)} service calls")

    # Пример поиска и массового комментирования
    search_filters = {
        "status": "new",
        "priority": "low"
    }

    results = bulk_ops.search_and_process(
        search_filters,
        lambda uuid: client.add_comment(uuid, "Автоматическое напоминание"),
    )
    print(f"Processed {len(results)} service calls")
