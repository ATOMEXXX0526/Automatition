"""
Базовые примеры использования Naumen Service Desk SDK
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from naumen_sdk import NaumenClient
from config import NAUMEN_URL, NAUMEN_API_KEY

# Создание клиента
client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)

# ========== Пример 1: Создание заявки ==========
print("=" * 50)
print("Пример 1: Создание заявки")
print("=" * 50)

service_call = client.create_service_call(
    title="Не работает принтер в офисе 305",
    description="Принтер HP LaserJet в офисе 305 не печатает документы. Горит красная лампочка.",
    client_uuid="client-uuid-here",  # Замените на реальный UUID
    priority="normal"
)

print(f"Создана заявка: {service_call.get('uuid')}")
print(f"Номер заявки: {service_call.get('number')}")
print()

# ========== Пример 2: Получение информации о заявке ==========
print("=" * 50)
print("Пример 2: Получение информации о заявке")
print("=" * 50)

# Используем UUID созданной заявки
service_call_uuid = service_call.get('uuid')
call_info = client.get_service_call(service_call_uuid)

print(f"Заявка: {call_info.get('title')}")
print(f"Статус: {call_info.get('status')}")
print(f"Приоритет: {call_info.get('priority')}")
print()

# ========== Пример 3: Добавление комментария ==========
print("=" * 50)
print("Пример 3: Добавление комментария")
print("=" * 50)

comment = client.add_comment(
    service_call_uuid,
    "Принтер был перезагружен, проблема сохраняется. Требуется замена картриджа.",
    is_private=False
)

print(f"Добавлен комментарий: {comment.get('uuid')}")
print()

# ========== Пример 4: Обновление заявки ==========
print("=" * 50)
print("Пример 4: Обновление заявки")
print("=" * 50)

updated_call = client.update_service_call(
    service_call_uuid,
    priority="high",
    description="ОБНОВЛЕНО: Принтер HP LaserJet в офисе 305 не печатает. Нужен новый картридж."
)

print(f"Заявка обновлена. Новый приоритет: {updated_call.get('priority')}")
print()

# ========== Пример 5: Поиск заявок ==========
print("=" * 50)
print("Пример 5: Поиск заявок")
print("=" * 50)

search_results = client.search_service_calls({
    "status": "new",
    "priority": "high"
})

print(f"Найдено заявок со статусом 'new' и приоритетом 'high': {len(search_results)}")

for call in search_results[:5]:  # Показываем первые 5
    print(f"  - {call.get('number')}: {call.get('title')}")
print()

# ========== Пример 6: Работа с пользователями ==========
print("=" * 50)
print("Пример 6: Поиск пользователей")
print("=" * 50)

users = client.search_users("Иванов", limit=10)

print(f"Найдено пользователей: {len(users)}")
for user in users[:3]:
    print(f"  - {user.get('fullName')} ({user.get('email')})")
print()

# ========== Пример 7: Закрытие заявки ==========
print("=" * 50)
print("Пример 7: Закрытие заявки")
print("=" * 50)

closed_call = client.close_service_call(
    service_call_uuid,
    resolution="Картридж заменен, принтер работает исправно."
)

print(f"Заявка закрыта: {closed_call.get('uuid')}")
print(f"Статус: {closed_call.get('status')}")
print()

print("=" * 50)
print("Все примеры выполнены успешно!")
print("=" * 50)
