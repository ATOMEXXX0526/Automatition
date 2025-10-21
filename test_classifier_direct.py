#!/usr/bin/env python3
"""
Прямое тестирование классификатора без Flask
"""
import sys
sys.path.insert(0, '/home/user/Automatition')

from ai_assistant.app.classifier import get_classifier

print("=" * 60)
print("AI Assistant - Тестирование классификатора")
print("=" * 60)
print()

# Получаем классификатор
classifier = get_classifier()

# Тестовые кейсы
test_cases = [
    {
        "id": "TEST-001",
        "subject": "Не работает Outlook",
        "description": "При запуске Outlook выдает ошибку и закрывается"
    },
    {
        "id": "TEST-002",
        "subject": "Нет доступа в интернет",
        "description": "Не могу подключиться к интернету, кабель подключен"
    },
    {
        "id": "TEST-003",
        "subject": "Ошибка в 1С",
        "description": "При запуске 1С Бухгалтерии выдает ошибку базы данных"
    },
    {
        "id": "TEST-004",
        "subject": "Принтер не печатает",
        "description": "Принтер HP не отвечает на команды печати"
    },
    {
        "id": "TEST-005",
        "subject": "Забыл пароль",
        "description": "Не могу войти в систему, забыл пароль"
    },
    {
        "id": "TEST-006",
        "subject": "КРИТИЧНО! Сервер недоступен",
        "description": "Все базы данных не работают, срочно нужна помощь"
    }
]

print("Тестирование классификации:\n")

for test in test_cases:
    print(f"{'=' * 60}")
    print(f"ID: {test['id']}")
    print(f"Тема: {test['subject']}")
    print(f"Описание: {test['description']}")
    print()

    # Классификация
    result = classifier.classify(test['subject'], test['description'])

    # Рекомендуемое действие
    action = classifier.get_suggested_action(result['confidence'])

    # Вывод результата
    print(f"Результат классификации:")
    print(f"  Категория:      {result['category']}")
    print(f"  Группа:         {result['support_group']}")
    print(f"  Приоритет:      {result['priority']}")
    print(f"  Уверенность:    {result['confidence']:.2%}")
    print(f"  Метод:          {result['method']}")
    print(f"  Действие:       {action}")

    if action == "auto_apply":
        print(f"  ✅ Автоматическое применение (confidence >= 80%)")
    elif action == "suggest":
        print(f"  💡 Рекомендация оператору (50% <= confidence < 80%)")
    else:
        print(f"  ⚠️  Ручная обработка (confidence < 50%)")

    print()

print("=" * 60)
print("✅ Тестирование завершено!")
print("=" * 60)
