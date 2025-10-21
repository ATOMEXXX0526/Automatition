# AI Assistant для Naumen Service Desk Pro - Локальный запуск

Интеллектуальный помощник для автоматической классификации и обработки заявок.

## Быстрый старт (3 команды)

```bash
cd ai_assistant

# 1. Установка и обучение модели
./setup.sh

# 2. Запуск сервера
./run.sh

# 3. Тестирование (в другом терминале)
./test_api.sh
```

## Пошаговая инструкция

### Шаг 1: Установка зависимостей

```bash
cd ai_assistant
pip3 install -r requirements.txt
```

**Требования:**
- Python 3.7+
- pip3

### Шаг 2: Обучение модели

```bash
python3 scripts/train_model.py
```

Это создаст файл `models/classifier_model.pkl` с обученными моделями.

**Ожидаемый результат:**
```
Training Category Classification Model
Accuracy on test set: 75%+
Models saved to models/classifier_model.pkl
```

### Шаг 3: Настройка (опционально)

Скопируйте пример конфигурации:
```bash
cp .env.example .env
```

Отредактируйте `.env`:
```bash
# Naumen Service Desk (опционально для тестирования)
NAUMEN_URL=https://your-naumen-server.com
NAUMEN_API_KEY=your-api-key-here

# Режим работы
DRY_RUN_MODE=true  # true = только логирование, false = применять изменения

# AI настройки
AUTO_APPLY_THRESHOLD=0.80
```

### Шаг 4: Запуск сервера

```bash
# С помощью скрипта
./run.sh

# Или напрямую
cd ..
PYTHONPATH=. python3 ai_assistant/app/main.py
```

**Сервер запустится на:** `http://localhost:5000`

### Шаг 5: Тестирование

В новом терминале:

```bash
# Автоматическое тестирование
./test_api.sh

# Или вручную
curl http://localhost:5000/health
```

## Примеры использования

### 1. Health Check

```bash
curl http://localhost:5000/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "service": "ai-assistant",
  "version": "1.0.0"
}
```

### 2. Классификация одной заявки

```bash
curl -X POST http://localhost:5000/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "INC-2025-0001",
    "subject": "Не работает Outlook",
    "description": "Outlook при запуске выдает ошибку"
  }'
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
  "applied": false,
  "processing_time_ms": 45.23
}
```

### 3. Batch обработка

```bash
curl -X POST http://localhost:5000/batch/classify \
  -H "Content-Type: application/json" \
  -d '{
    "tickets": [
      {
        "ticket_id": "INC-001",
        "subject": "Принтер не работает",
        "description": "Принтер не печатает документы"
      },
      {
        "ticket_id": "INC-002",
        "subject": "Забыл пароль",
        "description": "Нужно восстановить доступ"
      }
    ]
  }'
```

### 4. Тестирование с Python

```python
import requests

response = requests.post(
    'http://localhost:5000/ai/classify',
    json={
        'ticket_id': 'TEST-001',
        'subject': 'Не работает 1С',
        'description': 'При запуске 1С выдает ошибку базы данных'
    }
)

result = response.json()
print(f"Категория: {result['classification']['category']}")
print(f"Уверенность: {result['classification']['confidence']:.2%}")
print(f"Приоритет: {result['classification']['priority']}")
```

## Категории классификации

AI Assistant классифицирует заявки по следующим категориям:

| Категория | Ключевые слова | Группа поддержки |
|-----------|---------------|------------------|
| **Почта** | outlook, email, письмо, mail | 1 линия |
| **Сеть** | интернет, wifi, vpn, подключение | Сетевые администраторы |
| **1C** | 1c, бухгалтерия, зуп, erp | Специалисты 1C |
| **Оборудование** | принтер, сканер, монитор, клавиатура | 1 линия |
| **Доступ** | пароль, права, логин, доступ | Безопасность |
| **Прочее** | все остальное | 1 линия |

## Режимы работы

### DRY_RUN_MODE=true (Тестовый режим)

```bash
DRY_RUN_MODE=true ./run.sh
```

В этом режиме:
- ✅ Классификация работает
- ✅ Логи записываются
- ✅ Метрики собираются
- ❌ **НЕ** обновляет заявки в Naumen

**Используйте для тестирования!**

### DRY_RUN_MODE=false (Продакшн режим)

```bash
DRY_RUN_MODE=false ./run.sh
```

В этом режиме:
- ✅ Автоматически обновляет заявки в Naumen
- ⚠️ Требует настроенный `NAUMEN_API_KEY`

## Логи

Логи сохраняются в `ai_assistant.log` (JSON формат):

```bash
# Просмотр логов
tail -f ai_assistant.log

# Фильтрация по событиям
cat ai_assistant.log | grep "classification"
```

Пример лога:
```json
{
  "asctime": "2025-10-21 10:00:00",
  "levelname": "INFO",
  "message": "Classification completed",
  "ticket_id": "INC-2025-0001",
  "category": "Почта",
  "confidence": 0.85,
  "processing_time_ms": 45.23
}
```

## Метрики Prometheus

Доступны на: `http://localhost:5000/metrics`

```bash
curl http://localhost:5000/metrics
```

Основные метрики:
- `ai_assistant_requests_total` - Всего запросов
- `ai_assistant_auto_applied_total` - Автоприменений
- `ai_assistant_processing_latency_seconds` - Время обработки
- `ai_assistant_model_confidence` - Уверенность модели

## Структура проекта

```
ai_assistant/
├── app/
│   ├── main.py                  # Flask API
│   ├── classifier.py            # ML классификатор
│   ├── naumen_integration.py    # Интеграция с Naumen
│   ├── config.py               # Конфигурация
│   └── utils/
│       ├── logger.py           # Логирование
│       └── metrics.py          # Метрики
├── models/
│   └── classifier_model.pkl    # Обученная модель
├── data/
│   └── sample_tickets.json     # Тестовые данные
├── scripts/
│   └── train_model.py          # Обучение модели
├── tests/
│   └── test_classifier.py      # Тесты
├── setup.sh                     # Установка
├── run.sh                       # Запуск сервера
├── test_api.sh                  # Тестирование API
└── requirements.txt
```

## Тестирование

### Запуск pytest тестов

```bash
cd ai_assistant
pytest tests/test_classifier.py -v
```

### Ручное тестирование классификатора

```python
cd ai_assistant
python3

>>> from app.classifier import get_classifier
>>> classifier = get_classifier()
>>> result = classifier.classify("Не работает принтер", "Принтер не печатает")
>>> print(result)
{
  'category': 'Оборудование',
  'support_group': '1 линия',
  'priority': 'Normal',
  'confidence': 0.75,
  'method': 'rule_based'
}
```

## Обучение модели на своих данных

### 1. Подготовка данных

Создайте файл `data/my_training_data.json`:

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

### 2. Обновите скрипт обучения

В `scripts/train_model.py` измените путь к данным:

```python
sample_file = DATA_DIR / "my_training_data.json"
```

### 3. Запустите обучение

```bash
python3 scripts/train_model.py
```

### 4. Проверьте метрики

Скрипт выведет:
- Accuracy на test set
- Precision/Recall/F1 по классам
- Cross-validation scores

## Интеграция с Naumen

### 1. Получите API ключ

В Naumen admin console:
1. **Администрирование** → **Ключи API**
2. Создайте новый ключ
3. Скопируйте в `.env`:
   ```
   NAUMEN_API_KEY=your-key-here
   ```

### 2. Настройте Webhook (опционально)

В Naumen admin console:
1. **Администрирование** → **Шлюз взаимодействия**
2. URL: `http://your-server:5000/naumen/webhook`
3. Событие: `ticket_created`

### 3. Тест интеграции

```bash
# Установите DRY_RUN_MODE=false
DRY_RUN_MODE=false ./run.sh
```

## Troubleshooting

### Проблема: Модель не найдена

```
Model file not found: models/classifier_model.pkl
```

**Решение:**
```bash
python3 scripts/train_model.py
```

### Проблема: Import ошибка

```
ModuleNotFoundError: No module named 'app'
```

**Решение:**
```bash
cd ..
PYTHONPATH=. python3 ai_assistant/app/main.py
```

### Проблема: Порт занят

```
Address already in use
```

**Решение:**
```bash
# Найти процесс
lsof -i :5000

# Убить процесс
kill -9 <PID>

# Или использовать другой порт
FLASK_PORT=5001 ./run.sh
```

### Проблема: Низкая accuracy

**Решение:**
1. Добавьте больше тренировочных данных
2. Проверьте качество данных
3. Увеличьте разнообразие примеров

## FAQ

**Q: Работает ли без подключения к Naumen?**
A: Да! В режиме `DRY_RUN_MODE=true` можно тестировать без Naumen.

**Q: Сколько данных нужно для обучения?**
A: Минимум 20 примеров (уже есть), оптимально 100+ на категорию.

**Q: Можно ли добавить свои категории?**
A: Да, отредактируйте `app/config.py` → `CATEGORIES`.

**Q: Как повысить accuracy?**
A:
1. Добавьте больше данных
2. Улучшите предобработку текста
3. Используйте ruBERT вместо TF-IDF

**Q: Поддерживается ли Windows?**
A: Да, используйте Python напрямую:
```cmd
pip install -r requirements.txt
python scripts/train_model.py
set PYTHONPATH=.
python ai_assistant/app/main.py
```

## Следующие шаги

1. ✅ **Протестируйте локально** - используйте `./test_api.sh`
2. 📊 **Соберите реальные данные** - экспортируйте из Naumen
3. 🎓 **Обучите на реальных данных** - улучшите accuracy
4. 🔗 **Настройте интеграцию** - подключите к Naumen
5. 📈 **Мониторьте метрики** - отслеживайте качество

## Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f ai_assistant.log`
2. Проверьте health: `curl http://localhost:5000/health`
3. Создайте issue в GitHub

---

**Версия:** 1.0.0
**Дата:** 2025-10-21
