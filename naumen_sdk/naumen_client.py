"""
Naumen Service Desk Pro API Client
Клиент для работы с REST API Naumen Service Desk
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NaumenClient:
    """Клиент для работы с API Naumen Service Desk Pro"""

    def __init__(self, base_url: str, access_key: str, verify_ssl: bool = True):
        """
        Инициализация клиента

        Args:
            base_url: URL сервера Naumen (например, https://sd.company.com)
            access_key: Ключ доступа к API
            verify_ssl: Проверять SSL сертификат
        """
        self.base_url = base_url.rstrip('/')
        self.access_key = access_key
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_key}'
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Выполнить HTTP запрос к API

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Endpoint API
            **kwargs: Дополнительные параметры для requests

        Returns:
            Ответ от API в виде словаря
        """
        url = f"{self.base_url}/sd/services/rest/{endpoint}"
        kwargs['verify'] = self.verify_ssl

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            if response.content:
                return response.json()
            return {"status": "success"}

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise

    # ========== Работа с заявками (Service Calls) ==========

    def create_service_call(self,
                           title: str,
                           description: str,
                           client_uuid: str,
                           service_uuid: Optional[str] = None,
                           priority: str = "normal",
                           **kwargs) -> Dict:
        """
        Создать заявку

        Args:
            title: Заголовок заявки
            description: Описание заявки
            client_uuid: UUID клиента (заявителя)
            service_uuid: UUID услуги
            priority: Приоритет (low, normal, high, critical)
            **kwargs: Дополнительные поля

        Returns:
            Данные созданной заявки
        """
        data = {
            "title": title,
            "description": description,
            "client": client_uuid,
            "priority": priority,
            **kwargs
        }

        if service_uuid:
            data["service"] = service_uuid

        logger.info(f"Creating service call: {title}")
        return self._make_request('POST', 'create/serviceCall', json=data)

    def get_service_call(self, uuid: str) -> Dict:
        """
        Получить информацию о заявке

        Args:
            uuid: UUID заявки

        Returns:
            Данные заявки
        """
        return self._make_request('GET', f'get/serviceCall/{uuid}')

    def update_service_call(self, uuid: str, **fields) -> Dict:
        """
        Обновить заявку

        Args:
            uuid: UUID заявки
            **fields: Поля для обновления

        Returns:
            Обновленные данные заявки
        """
        logger.info(f"Updating service call {uuid}")
        return self._make_request('PUT', f'edit/serviceCall/{uuid}', json=fields)

    def close_service_call(self, uuid: str, resolution: str) -> Dict:
        """
        Закрыть заявку

        Args:
            uuid: UUID заявки
            resolution: Решение/комментарий при закрытии

        Returns:
            Данные закрытой заявки
        """
        logger.info(f"Closing service call {uuid}")
        return self._make_request('POST', f'close/serviceCall/{uuid}',
                                 json={"resolution": resolution})

    def search_service_calls(self, filters: Dict) -> List[Dict]:
        """
        Поиск заявок по фильтрам

        Args:
            filters: Словарь с фильтрами для поиска

        Returns:
            Список найденных заявок
        """
        return self._make_request('POST', 'search/serviceCall', json=filters)

    # ========== Работа с инцидентами ==========

    def create_incident(self,
                       title: str,
                       description: str,
                       client_uuid: str,
                       service_uuid: Optional[str] = None,
                       urgency: str = "normal",
                       impact: str = "normal",
                       **kwargs) -> Dict:
        """
        Создать инцидент

        Args:
            title: Заголовок инцидента
            description: Описание инцидента
            client_uuid: UUID клиента
            service_uuid: UUID услуги
            urgency: Срочность (low, normal, high, critical)
            impact: Влияние (low, normal, high, critical)
            **kwargs: Дополнительные поля

        Returns:
            Данные созданного инцидента
        """
        data = {
            "title": title,
            "description": description,
            "client": client_uuid,
            "urgency": urgency,
            "impact": impact,
            **kwargs
        }

        if service_uuid:
            data["service"] = service_uuid

        logger.info(f"Creating incident: {title}")
        return self._make_request('POST', 'create/incident', json=data)

    # ========== Работа с комментариями ==========

    def add_comment(self, object_uuid: str, text: str, is_private: bool = False) -> Dict:
        """
        Добавить комментарий к объекту

        Args:
            object_uuid: UUID объекта (заявки, инцидента и т.д.)
            text: Текст комментария
            is_private: Является ли комментарий внутренним

        Returns:
            Данные созданного комментария
        """
        data = {
            "object": object_uuid,
            "text": text,
            "isPrivate": is_private
        }

        return self._make_request('POST', 'create/comment', json=data)

    def get_comments(self, object_uuid: str) -> List[Dict]:
        """
        Получить комментарии объекта

        Args:
            object_uuid: UUID объекта

        Returns:
            Список комментариев
        """
        return self._make_request('GET', f'list/comments/{object_uuid}')

    # ========== Работа с вложениями ==========

    def attach_file(self, object_uuid: str, file_path: str, description: str = "") -> Dict:
        """
        Прикрепить файл к объекту

        Args:
            object_uuid: UUID объекта
            file_path: Путь к файлу
            description: Описание вложения

        Returns:
            Данные вложения
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'object': object_uuid,
                'description': description
            }

            url = f"{self.base_url}/sd/services/rest/attach/file"
            response = self.session.post(url, data=data, files=files,
                                        verify=self.verify_ssl)
            response.raise_for_status()
            return response.json()

    # ========== Работа с пользователями и группами ==========

    def get_user(self, uuid: str) -> Dict:
        """
        Получить информацию о пользователе

        Args:
            uuid: UUID пользователя

        Returns:
            Данные пользователя
        """
        return self._make_request('GET', f'get/employee/{uuid}')

    def search_users(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Поиск пользователей

        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов

        Returns:
            Список найденных пользователей
        """
        filters = {
            "query": query,
            "limit": limit
        }
        return self._make_request('POST', 'search/employee', json=filters)

    def get_team(self, uuid: str) -> Dict:
        """
        Получить информацию о команде/группе

        Args:
            uuid: UUID команды

        Returns:
            Данные команды
        """
        return self._make_request('GET', f'get/team/{uuid}')

    # ========== Работа с услугами и каталогом ==========

    def get_service(self, uuid: str) -> Dict:
        """
        Получить информацию об услуге

        Args:
            uuid: UUID услуги

        Returns:
            Данные услуги
        """
        return self._make_request('GET', f'get/service/{uuid}')

    def get_service_catalog(self) -> List[Dict]:
        """
        Получить каталог услуг

        Returns:
            Список услуг из каталога
        """
        return self._make_request('GET', 'list/serviceCatalog')

    # ========== Отчеты и аналитика ==========

    def get_report(self, report_uuid: str, parameters: Optional[Dict] = None) -> Any:
        """
        Получить отчет

        Args:
            report_uuid: UUID отчета
            parameters: Параметры отчета

        Returns:
            Данные отчета
        """
        data = {"parameters": parameters or {}}
        return self._make_request('POST', f'report/{report_uuid}', json=data)

    # ========== Утилиты ==========

    def execute_script(self, script_uuid: str, parameters: Optional[Dict] = None) -> Dict:
        """
        Выполнить серверный скрипт

        Args:
            script_uuid: UUID скрипта
            parameters: Параметры скрипта

        Returns:
            Результат выполнения скрипта
        """
        data = {"parameters": parameters or {}}
        return self._make_request('POST', f'execute/script/{script_uuid}', json=data)

    def get_object_by_fqn(self, fqn: str) -> Dict:
        """
        Получить объект по FQN (Fully Qualified Name)

        Args:
            fqn: Полное имя объекта

        Returns:
            Данные объекта
        """
        return self._make_request('GET', f'get/fqn/{fqn}')
