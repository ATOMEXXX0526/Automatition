# AI Assistant для Naumen Service Desk Pro

Интеллектуальный помощник для автоматической классификации и обработки заявок в Naumen Service Desk Pro.

## Возможности

- **Автоматическая классификация** заявок по категориям (Почта, Сеть, 1C, Оборудование, Доступ)
- **Определение приоритета** (Low, Normal, High, Critical)
- **Назначение группы поддержки** на основе категории
- **Автоприменение** изменений при высокой уверенности (configurable threshold)
- **Webhook интеграция** с Naumen для real-time обработки
- **Batch API** для массовой обработки заявок
- **Prometheus метрики** для мониторинга
- **Детальное логирование** всех операций

## Архитектура

```
Naumen Service Desk
        ↓
    Webhook (ticket_created)
        ↓
AI Assistant (Flask API)
        ↓
   TF-IDF Classifier
        ↓
   Classification Result
        ↓
Naumen API (update ticket)
```

## Структура проекта

```
ai_assistant/
├── app/
│   ├── main.py                  # Flask API endpoints
│   ├── classifier.py            # ML классификатор
│   ├── naumen_integration.py    # Интеграция с Naumen
│   ├── config.py               # Конфигурация
│   └── utils/
│       ├── logger.py           # Логирование
│       └── metrics.py          # Prometheus метрики
├── models/                      # Обученные ML модели
├── data/                        # Тестовые данные
├── scripts/
│   └── train_model.py          # Скрипт обучения модели
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Установка и запуск

### 1. Подготовка

Клонируйте репозиторий:
```bash
git clone https://github.com/ATOMEXXX0526/Automatition.git
cd Automatition/ai_assistant
```

### 2. Обучение модели

Перед первым запуском необходимо обучить модель:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Обучение модели на тестовых данных
python scripts/train_model.py
```

Это создаст файл `models/classifier_model.pkl` с обученными моделями.

### 3. Конфигурация

Скопируйте пример конфигурации:
```bash
cp .env.example .env
```

Отредактируйте `.env`:
```bash
# Naumen Service Desk
NAUMEN_URL=https://your-naumen-server.com
NAUMEN_API_KEY=your-api-key-here
NAUMEN_VERIFY_SSL=true

# AI настройки
AUTO_APPLY_THRESHOLD=0.80        # Порог автоприменения (0.0-1.0)
MIN_CONFIDENCE_THRESHOLD=0.50    # Минимальная уверенность

# Режим работы
DRY_RUN_MODE=false              # true = только логировать, не применять
```

### 4. Запуск с Docker

```bash
# Сборка и запуск
docker-compose up -d

# Проверка логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 5. Запуск без Docker

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск Flask приложения
python -m app.main

# Или с gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app.main:app
```

## API Endpoints

### Health Check

```bash
GET /health
```

**Ответ:**
```json
{
  "status": "healthy",
  "service": "ai-assistant",
  "version": "1.0.0"
}
```

### Классификация заявки

```bash
POST /ai/classify
Content-Type: application/json

{
  "ticket_id": "INC-2025-0001",
  "subject": "Не работает Outlook",
  "description": "Outlook при запуске выдает ошибку и закрывается"
}
```

**Ответ:**
```json
{
  "ticket_id": "INC-2025-0001",
  "classification": {
    "category": "Почта",
    "support_group": "1 линия",
    "priority": "High",
    "confidence": 0.85,
    "method": "rule_based"
  },
  "action": "auto_apply",
  "applied": true,
  "processing_time_ms": 123.45
}
```

### Webhook от Naumen

```bash
POST /naumen/webhook
Content-Type: application/json

{
  "event": "ticket_created",
  "ticket": {
    "id": "INC-2025-0001",
    "subject": "Проблема с сетью",
    "description": "Нет доступа в интернет",
    "requester": {"id": "u123", "name": "Иванов"},
    "created_at": "2025-10-21T10:00:00Z"
  }
}
```

### Batch классификация

```bash
POST /batch/classify
Content-Type: application/json

{
  "tickets": [
    {
      "ticket_id": "INC-001",
      "subject": "Не работает принтер",
      "description": "Принтер не печатает"
    },
    {
      "ticket_id": "INC-002",
      "subject": "Нет доступа к папке",
      "description": "Нужны права на сетевую папку"
    }
  ]
}
```

### Prometheus метрики

```bash
GET /metrics
```

## Примеры использования

### Python

```python
import requests

# Классификация одной заявки
response = requests.post(
    'http://localhost:5000/ai/classify',
    json={
        'ticket_id': 'INC-2025-0001',
        'subject': 'Не работает 1С',
        'description': 'При запуске 1С выдает ошибку подключения к базе'
    }
)

result = response.json()
print(f"Категория: {result['classification']['category']}")
print(f"Уверенность: {result['classification']['confidence']:.2%}")
print(f"Действие: {result['action']}")
```

### cURL

```bash
# Классификация
curl -X POST http://localhost:5000/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "INC-2025-0001",
    "subject": "Не работает почта",
    "description": "Outlook не открывается"
  }'

# Health check
curl http://localhost:5000/health

# Метрики
curl http://localhost:5000/metrics
```

## Интеграция с Naumen

### 1. Создание API ключа

В Naumen admin console:
1. Перейдите в **Администрирование** → **Ключи API**
2. Создайте новый ключ для сервисного аккаунта
3. Назначьте необходимые права (чтение/запись заявок, добавление комментариев)
4. Скопируйте ключ в `.env` файл

### 2. Настройка Webhook

В Naumen admin console:
1. Перейдите в **Администрирование** → **Шлюз взаимодействия**
2. Создайте новый шлюз:
   - **Тип**: HTTP POST
   - **URL**: `http://your-ai-assistant-server:5000/naumen/webhook`
   - **Событие**: Создание заявки (ticket_created)
   - **Формат**: JSON

3. Настройте payload:
```json
{
  "event": "ticket_created",
  "ticket": {
    "id": "${ticket.id}",
    "subject": "${ticket.subject}",
    "description": "${ticket.description}",
    "requester": {
      "id": "${ticket.requester.id}",
      "name": "${ticket.requester.name}"
    },
    "created_at": "${ticket.createdAt}"
  }
}
```

### 3. Fallback: Polling режим

Если webhook недоступен, используйте cron для периодической обработки:

```bash
# Скрипт для cron (пример)
*/5 * * * * python /path/to/poll_naumen.py
```

## Мониторинг и метрики

### Prometheus метрики

AI Assistant экспортирует следующие метрики:

- `ai_assistant_requests_total{status}` - Всего запросов (success/error)
- `ai_assistant_auto_applied_total{category}` - Автоприменений по категориям
- `ai_assistant_errors_total{error_type}` - Ошибки по типам
- `ai_assistant_processing_latency_seconds` - Время обработки (histogram)
- `ai_assistant_model_confidence` - Распределение уверенности модели
- `ai_assistant_active_requests` - Активные запросы

### Запуск Prometheus и Grafana

```bash
# С monitoring profile
docker-compose --profile monitoring up -d

# Prometheus UI: http://localhost:9091
# Grafana UI: http://localhost:3000 (admin/admin)
```

### Логирование

Логи сохраняются в JSON формате в файл `ai_assistant.log`:

```json
{
  "asctime": "2025-10-21 10:00:00",
  "name": "ai_assistant",
  "levelname": "INFO",
  "message": "Classification completed",
  "event": "classification",
  "ticket_id": "INC-2025-0001",
  "category": "Почта",
  "confidence": 0.85,
  "processing_time_ms": 123.45,
  "auto_applied": true
}
```

## Обучение модели на реальных данных

### 1. Экспорт данных из Naumen

Выгрузите исторические заявки в CSV/JSON:

```json
[
  {
    "subject": "...",
    "description": "...",
    "category": "Почта",
    "priority": "High"
  },
  ...
]
```

### 2. Обучение

```bash
# Положите данные в data/training_data.json
python scripts/train_model.py
```

### 3. Метрики модели

Скрипт выведет:
- Accuracy на test set
- Classification report (precision, recall, F1-score)
- Cross-validation scores

### 4. Регулярное переобучение

Настройте периодическое переобучение (например, еженедельно):

```bash
# Cron example
0 2 * * 0 /usr/bin/python3 /path/to/train_model.py
```

## Настройка порогов

### AUTO_APPLY_THRESHOLD (default: 0.80)

Порог уверенности для автоматического применения:
- `>= 0.80` → автоприменение
- `< 0.80` → только рекомендация в комментарии

Рекомендации:
- **Высокая точность**: 0.90+ (меньше автоприменений, но надежнее)
- **Баланс**: 0.80 (рекомендуется)
- **Агрессивный**: 0.70 (больше автоматизации, но возможны ошибки)

### MIN_CONFIDENCE_THRESHOLD (default: 0.50)

Минимальная уверенность для отображения рекомендации:
- `>= 0.50` → показать рекомендацию
- `< 0.50` → ручная обработка

## Режимы работы

### DRY_RUN_MODE

```bash
DRY_RUN_MODE=true
```

В этом режиме AI Assistant:
- ✅ Классифицирует заявки
- ✅ Логирует все решения
- ✅ Собирает метрики
- ❌ **НЕ** обновляет заявки в Naumen

Используйте для:
- Тестирования
- Валидации модели
- Проверки интеграции

## Безопасность

1. **API ключи**: Храните в переменных окружения, не коммитьте в Git
2. **HTTPS**: Используйте SSL/TLS для всех соединений
3. **Права доступа**: Минимальные необходимые права для сервисного аккаунта
4. **Webhook secret**: Добавьте проверку подписи webhook (опционально)
5. **Rate limiting**: Настройте ограничение запросов (в nginx/API gateway)

## Производительность

- **Время обработки**: < 1 секунда (baseline TF-IDF)
- **Throughput**: ~100 запросов/мин (4 workers)
- **Память**: ~500 MB (с загруженной моделью)

### Масштабирование

Увеличьте количество workers:
```bash
gunicorn --workers 8 --threads 2 app.main:app
```

Или используйте горизонтальное масштабирование с балансировщиком.

## Troubleshooting

### Модель не найдена

```
Model file not found: models/classifier_model.pkl
```

**Решение**: Обучите модель:
```bash
python scripts/train_model.py
```

### Ошибка подключения к Naumen

```
Failed to initialize Naumen client
```

**Решение**: Проверьте:
- NAUMEN_URL корректный
- NAUMEN_API_KEY валидный
- Сеть доступна
- SSL сертификат валиден (или установите `NAUMEN_VERIFY_SSL=false`)

### Низкая accuracy

```
Accuracy on test set: 45%
```

**Решение**:
- Добавьте больше тренировочных данных
- Улучшите предобработку текста
- Попробуйте другие модели (RandomForest, SVM)
- Рассмотрите использование ruBERT

## Roadmap

- [ ] Поддержка ruBERT/transformers для повышения accuracy
- [ ] Автоматическое дообучение на feedback (reinforcement learning)
- [ ] Определение дубликатов заявок
- [ ] Автоматические ответы на типовые запросы
- [ ] Интеграция с Telegram/Slack для уведомлений
- [ ] Web UI для мониторинга
- [ ] A/B тестирование моделей

## Лицензия

MIT License

## Поддержка

Если возникли вопросы или проблемы:
1. Проверьте логи: `docker-compose logs ai-assistant`
2. Просмотрите метрики: `http://localhost:9090/metrics`
3. Создайте issue в GitHub репозитории

---

**Разработано для автоматизации Naumen Service Desk Pro**
