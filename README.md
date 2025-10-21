# Naumen Service Desk Pro - Автоматизация

Комплексное решение для автоматизации работы с Naumen Service Desk Pro через REST API.

## Возможности

- **API клиент** - полнофункциональный Python клиент для работы с REST API Naumen Service Desk
- **Автоматическая обработка инцидентов** - классификация, назначение и эскалация
- **Массовые операции** - обработка множества заявок одновременно
- **Мониторинг SLA** - автоматический контроль соблюдения SLA и эскалация
- **Шаблоны заявок** - создание заявок по шаблонам с переменными
- **Планировщик задач** - готовые скрипты для автоматизации рутинных операций

## Структура проекта

```
Automatition/
├── naumen_sdk/              # SDK для работы с API
│   ├── __init__.py
│   └── naumen_client.py     # Основной клиент API
├── automation/              # Модули автоматизации
│   ├── auto_incident_handler.py  # Автообработка инцидентов
│   ├── bulk_operations.py        # Массовые операции
│   └── sla_monitor.py            # Мониторинг SLA
├── examples/                # Примеры использования
│   ├── basic_usage.py            # Базовые примеры
│   ├── advanced_automation.py    # Продвинутая автоматизация
│   └── scheduled_tasks.py        # Планируемые задачи
├── config.py.example        # Пример конфигурации
├── requirements.txt         # Зависимости Python
└── README.md               # Документация
```

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/ATOMEXXX0526/Automatition.git
cd Automatition
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка конфигурации

Скопируйте файл конфигурации и заполните своими данными:

```bash
cp config.py.example config.py
```

Отредактируйте `config.py`:

```python
NAUMEN_URL = "https://your-naumen-server.com"
NAUMEN_API_KEY = "your-api-key-here"
```

## Быстрый старт

### Базовое использование API

```python
from naumen_sdk import NaumenClient

# Создание клиента
client = NaumenClient("https://your-server.com", "your-api-key")

# Создание заявки
service_call = client.create_service_call(
    title="Не работает принтер",
    description="Принтер не печатает документы",
    client_uuid="client-uuid",
    priority="normal"
)

# Добавление комментария
client.add_comment(
    service_call['uuid'],
    "Принтер был перезагружен"
)

# Закрытие заявки
client.close_service_call(
    service_call['uuid'],
    resolution="Проблема решена"
)
```

### Автоматическая обработка инцидентов

```python
from naumen_sdk import NaumenClient
from automation.auto_incident_handler import IncidentHandler

client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)
handler = IncidentHandler(client)

# Создание инцидента с автоклассификацией
team_mapping = {
    "сеть": "network-team-uuid",
    "1c": "1c-team-uuid",
}

incident = handler.create_smart_incident(
    title="Критическая проблема с сетью",
    description="Не работает интернет во всем офисе",
    client_uuid="client-uuid",
    team_mapping=team_mapping
)
# Приоритет и команда будут назначены автоматически!
```

### Массовые операции

```python
from automation.bulk_operations import BulkOperations

bulk_ops = BulkOperations(client)

# Массовое обновление приоритета
uuids = ["uuid1", "uuid2", "uuid3"]
bulk_ops.bulk_update(uuids, {"priority": "high"})

# Массовое добавление комментариев
bulk_ops.bulk_comment(
    uuids,
    "Напоминание о необходимости обновления информации"
)

# Поиск и массовая обработка
results = bulk_ops.search_and_process(
    {"status": "new", "priority": "low"},
    lambda uuid: client.update_service_call(uuid, priority="normal")
)
```

### Мониторинг SLA

```python
from automation.sla_monitor import SLAMonitor

sla_monitor = SLAMonitor(client)

# Проверка нарушений SLA
breaches = sla_monitor.check_sla_breaches()
print(f"Нарушений SLA: {len(breaches)}")

# Отправка предупреждений (при 80% времени SLA)
warnings = sla_monitor.send_sla_warnings(warning_threshold=0.8)

# Автоматическая эскалация нарушений
escalated = sla_monitor.auto_escalate_breaches()

# Генерация отчета
report = sla_monitor.generate_sla_report()
print(f"SLA соблюден: {report['sla_compliance_rate']:.2f}%")
```

## API клиент - Документация

### NaumenClient

Основной класс для работы с API Naumen Service Desk.

#### Инициализация

```python
client = NaumenClient(
    base_url="https://sd.company.com",
    access_key="your-api-key",
    verify_ssl=True  # Опционально
)
```

#### Методы работы с заявками

##### create_service_call()

Создание заявки.

```python
service_call = client.create_service_call(
    title="Заголовок заявки",
    description="Описание проблемы",
    client_uuid="uuid-клиента",
    service_uuid="uuid-услуги",  # опционально
    priority="normal",  # low, normal, high, critical
    # Дополнительные поля
    custom_field="value"
)
```

##### get_service_call()

Получение информации о заявке.

```python
call_info = client.get_service_call("service-call-uuid")
```

##### update_service_call()

Обновление заявки.

```python
client.update_service_call(
    "service-call-uuid",
    priority="high",
    description="Обновленное описание",
    assignee="assignee-uuid"
)
```

##### close_service_call()

Закрытие заявки.

```python
client.close_service_call(
    "service-call-uuid",
    resolution="Проблема решена путем..."
)
```

##### search_service_calls()

Поиск заявок по фильтрам.

```python
results = client.search_service_calls({
    "status": ["new", "in_progress"],
    "priority": "high",
    "assignee": "assignee-uuid"
})
```

#### Методы работы с инцидентами

##### create_incident()

Создание инцидента.

```python
incident = client.create_incident(
    title="Заголовок инцидента",
    description="Описание",
    client_uuid="client-uuid",
    urgency="high",  # low, normal, high, critical
    impact="high"
)
```

#### Методы работы с комментариями

##### add_comment()

Добавление комментария.

```python
client.add_comment(
    "object-uuid",
    "Текст комментария",
    is_private=False  # True для внутреннего комментария
)
```

##### get_comments()

Получение комментариев объекта.

```python
comments = client.get_comments("object-uuid")
```

#### Методы работы с вложениями

##### attach_file()

Прикрепление файла к объекту.

```python
client.attach_file(
    "object-uuid",
    "/path/to/file.pdf",
    description="Описание вложения"
)
```

#### Методы работы с пользователями

##### get_user()

Получение информации о пользователе.

```python
user = client.get_user("user-uuid")
```

##### search_users()

Поиск пользователей.

```python
users = client.search_users("Иванов", limit=50)
```

## Автоматизация

### IncidentHandler - Автообработчик инцидентов

#### auto_classify_priority()

Автоматическое определение приоритета на основе ключевых слов.

```python
priority = handler.auto_classify_priority(
    "Критический сбой системы",
    "Все серверы недоступны"
)
# Вернет: "critical"
```

#### create_smart_incident()

Создание инцидента с автоклассификацией и назначением.

```python
incident = handler.create_smart_incident(
    title="Проблема с 1C",
    description="Не открывается база данных",
    client_uuid="client-uuid",
    team_mapping={"1c": "team-uuid"}
)
```

#### monitor_and_escalate()

Мониторинг и эскалация старых инцидентов.

```python
escalated = handler.monitor_and_escalate(
    filters={"status": "new"},
    escalation_hours=24
)
```

### BulkOperations - Массовые операции

#### bulk_update()

Массовое обновление заявок.

```python
results = bulk_ops.bulk_update(
    ["uuid1", "uuid2"],
    {"priority": "high"},
    delay=0.5  # задержка между запросами
)
```

#### bulk_close()

Массовое закрытие заявок.

```python
results = bulk_ops.bulk_close(
    ["uuid1", "uuid2"],
    resolution="Решено автоматически"
)
```

#### search_and_process()

Поиск и обработка найденных заявок.

```python
results = bulk_ops.search_and_process(
    {"status": "new"},
    lambda uuid: client.add_comment(uuid, "Комментарий")
)
```

### SLAMonitor - Мониторинг SLA

#### check_sla_breaches()

Проверка нарушений SLA.

```python
breaches = sla_monitor.check_sla_breaches(
    filters={"status": ["new", "in_progress"]}
)
```

#### send_sla_warnings()

Отправка предупреждений о приближении к нарушению.

```python
warnings = sla_monitor.send_sla_warnings(
    warning_threshold=0.8  # при 80% времени
)
```

#### auto_escalate_breaches()

Автоматическая эскалация нарушений.

```python
escalated = sla_monitor.auto_escalate_breaches()
```

#### generate_sla_report()

Генерация отчета по SLA.

```python
from datetime import datetime, timedelta

report = sla_monitor.generate_sla_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)
```

## Планировщик задач

Для автоматизации рутинных операций используйте готовые скрипты из `examples/scheduled_tasks.py`.

### Настройка cron

```bash
# Проверка SLA каждые 15 минут
*/15 * * * * /usr/bin/python3 /path/to/scheduled_tasks.py sla_check

# Эскалация старых инцидентов каждый час
0 * * * * /usr/bin/python3 /path/to/scheduled_tasks.py escalate_old

# Ежедневный отчет в 9:00
0 9 * * * /usr/bin/python3 /path/to/scheduled_tasks.py daily_report

# Мониторинг неназначенных каждые 30 минут
*/30 * * * * /usr/bin/python3 /path/to/scheduled_tasks.py monitor_unassigned
```

### Доступные задачи

- `sla_check` - Проверка SLA, отправка предупреждений и автоэскалация
- `escalate_old` - Эскалация инцидентов старше 24 часов
- `daily_report` - Генерация ежедневного отчета по SLA
- `cleanup` - Очистка тестовых данных
- `monitor_unassigned` - Мониторинг неназначенных заявок

## Примеры использования

### Пример 1: Базовые операции

Запустите `examples/basic_usage.py` для демонстрации базовых операций:

```bash
python examples/basic_usage.py
```

### Пример 2: Продвинутая автоматизация

Запустите `examples/advanced_automation.py` для демонстрации всех возможностей:

```bash
python examples/advanced_automation.py
```

## Лучшие практики

### 1. Безопасность

- Храните API ключи в переменных окружения или защищенном хранилище
- Не коммитьте `config.py` в Git
- Используйте SSL/TLS для всех соединений

### 2. Производительность

- Используйте задержки между массовыми операциями
- Ограничивайте количество параллельных потоков (max_workers)
- Кэшируйте часто используемые данные (UUID команд, услуг и т.д.)

### 3. Надежность

- Обрабатывайте исключения в продакшн коде
- Логируйте все операции
- Используйте retry механизм для критичных операций

### 4. Мониторинг

- Регулярно проверяйте логи автоматизации
- Настройте алерты для критичных ошибок
- Мониторьте производительность API запросов

## Обработка ошибок

```python
from naumen_sdk import NaumenClient
import logging

logger = logging.getLogger(__name__)

try:
    client = NaumenClient(NAUMEN_URL, NAUMEN_API_KEY)
    service_call = client.create_service_call(
        title="Тест",
        description="Тестовая заявка",
        client_uuid="invalid-uuid"
    )
except Exception as e:
    logger.error(f"Failed to create service call: {e}")
    # Обработка ошибки
```

## Логирование

Настройка логирования в вашем приложении:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('naumen_automation.log'),
        logging.StreamHandler()
    ]
)
```

## Требования

- Python 3.7+
- requests 2.25.0+
- Naumen Service Desk Pro с включенным REST API

## Лицензия

MIT License

## Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте документацию Naumen Service Desk API
2. Просмотрите примеры в директории `examples/`
3. Создайте issue в репозитории GitHub

## Roadmap

- [ ] Интеграция с webhook
- [ ] Поддержка GraphQL API
- [ ] CLI интерфейс
- [ ] Docker контейнер
- [ ] Дополнительные отчеты
- [ ] Email уведомления
- [ ] Telegram бот для управления

## Changelog

### v1.0.0 (2025-10-21)

- Начальная версия
- API клиент для Naumen Service Desk
- Автоматическая обработка инцидентов
- Массовые операции
- Мониторинг SLA
- Примеры использования
- Планировщик задач

## Авторы

Автоматизация разработана для упрощения работы с Naumen Service Desk Pro.

## Благодарности

Спасибо всем, кто использует и улучшает этот проект!
