#!/bin/bash
# Скрипт тестирования API

API_URL=${1:-http://localhost:5000}

echo "=========================================="
echo "AI Assistant - Тестирование API"
echo "=========================================="
echo "API URL: $API_URL"
echo ""

# 1. Health Check
echo "1. Health Check..."
curl -s $API_URL/health | python3 -m json.tool
echo ""

# 2. Тест классификации - Почта
echo "2. Тест: Проблема с почтой..."
curl -s -X POST $API_URL/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "subject": "Не работает Outlook",
    "description": "При запуске Outlook выдает ошибку и закрывается"
  }' | python3 -m json.tool
echo ""

# 3. Тест классификации - Сеть
echo "3. Тест: Проблема с сетью..."
curl -s -X POST $API_URL/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-002",
    "subject": "Нет доступа в интернет",
    "description": "Не могу подключиться к интернету, кабель подключен"
  }' | python3 -m json.tool
echo ""

# 4. Тест классификации - 1C
echo "4. Тест: Проблема с 1С..."
curl -s -X POST $API_URL/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-003",
    "subject": "Ошибка в 1С",
    "description": "При запуске 1С Бухгалтерии выдает ошибку базы данных"
  }' | python3 -m json.tool
echo ""

# 5. Тест классификации - Оборудование
echo "5. Тест: Проблема с оборудованием..."
curl -s -X POST $API_URL/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-004",
    "subject": "Принтер не печатает",
    "description": "Принтер HP не отвечает на команды печати"
  }' | python3 -m json.tool
echo ""

# 6. Тест Batch API
echo "6. Тест: Batch обработка..."
curl -s -X POST $API_URL/batch/classify \
  -H "Content-Type: application/json" \
  -d '{
    "tickets": [
      {
        "ticket_id": "BATCH-001",
        "subject": "Забыл пароль",
        "description": "Не могу войти в систему"
      },
      {
        "ticket_id": "BATCH-002",
        "subject": "WiFi не работает",
        "description": "Слабый сигнал WiFi в офисе"
      }
    ]
  }' | python3 -m json.tool
echo ""

echo "=========================================="
echo "✅ Тестирование завершено!"
echo "=========================================="
