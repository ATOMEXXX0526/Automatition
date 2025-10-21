# AI Assistant - Установка и запуск на Windows

## Быстрый старт

### Вариант 1: Автоматический (Рекомендуется)

1. **Откройте PowerShell в папке проекта**
   ```powershell
   cd D:\das\Automatition
   ```

2. **Запустите bat-файл**
   ```cmd
   run_windows.bat
   ```

Скрипт автоматически:
- ✅ Создаст config.py
- ✅ Обучит модель (если нужно)
- ✅ Запустит сервер

---

### Вариант 2: Пошаговая установка

#### Шаг 1: Создайте config.py

```powershell
# PowerShell
Copy-Item config.py.example ai_assistant\app\config.py
```

или

```cmd
REM CMD
copy config.py.example ai_assistant\app\config.py
```

#### Шаг 2: Установите зависимости (если еще не установлены)

```powershell
pip install -r ai_assistant\requirements.txt
```

#### Шаг 3: Обучите модель

```powershell
python ai_assistant\scripts\train_model.py
```

#### Шаг 4: Настройте конфигурацию (опционально)

Отредактируйте `ai_assistant\app\config.py`:

```python
# Naumen Service Desk
NAUMEN_URL = "https://your-naumen-server.com"
NAUMEN_API_KEY = "your-api-key-here"

# Режим работы
DRY_RUN_MODE = True  # True = только тестирование
```

#### Шаг 5: Запустите сервер

```powershell
# Установите PYTHONPATH
$env:PYTHONPATH = (Get-Location).Path

# Запустите
python run_ai_assistant.py
```

или в CMD:

```cmd
set PYTHONPATH=%CD%
python run_ai_assistant.py
```

---

## Проверка работы

### 1. Health Check

Откройте новое окно PowerShell:

```powershell
curl http://localhost:5000/health
```

или в браузере:
```
http://localhost:5000/health
```

### 2. Тест классификации

```powershell
# PowerShell
Invoke-RestMethod -Uri http://localhost:5000/ai/classify -Method Post -ContentType "application/json" -Body '{"ticket_id":"TEST-001","subject":"Не работает Outlook","description":"Ошибка при запуске"}'
```

или через curl (если установлен):

```cmd
curl -X POST http://localhost:5000/ai/classify -H "Content-Type: application/json" -d "{\"ticket_id\":\"TEST-001\",\"subject\":\"Не работает принтер\",\"description\":\"HP не печатает\"}"
```

### 3. Прямое тестирование классификатора

```powershell
python test_classifier_direct.py
```

---

## Частые проблемы на Windows

### Проблема 1: ModuleNotFoundError: No module named 'ai_assistant.app.config'

**Решение:**
```powershell
# Создайте config.py
Copy-Item config.py.example ai_assistant\app\config.py
```

### Проблема 2: No module named 'ai_assistant'

**Решение:**
```powershell
# PowerShell
$env:PYTHONPATH = (Get-Location).Path
python run_ai_assistant.py

# CMD
set PYTHONPATH=%CD%
python run_ai_assistant.py
```

### Проблема 3: Модель не найдена

**Решение:**
```powershell
python ai_assistant\scripts\train_model.py
```

### Проблема 4: Порт 5000 занят

**Решение:**
```powershell
# PowerShell
$env:FLASK_PORT = "5001"
python run_ai_assistant.py

# CMD
set FLASK_PORT=5001
python run_ai_assistant.py
```

### Проблема 5: Ошибки с кодировкой UTF-8

**Решение:**
```powershell
# PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
python run_ai_assistant.py

# CMD
set PYTHONIOENCODING=utf-8
python run_ai_assistant.py
```

---

## Переменные окружения для Windows

### PowerShell

```powershell
# Базовые
$env:PYTHONPATH = (Get-Location).Path
$env:DRY_RUN_MODE = "true"
$env:FLASK_PORT = "5000"

# Naumen (если нужно)
$env:NAUMEN_URL = "https://your-naumen.com"
$env:NAUMEN_API_KEY = "your-key"

# Запуск
python run_ai_assistant.py
```

### CMD

```cmd
set PYTHONPATH=%CD%
set DRY_RUN_MODE=true
set FLASK_PORT=5000
set NAUMEN_URL=https://your-naumen.com
set NAUMEN_API_KEY=your-key
python run_ai_assistant.py
```

---

## Автозапуск на Windows

### Вариант 1: Task Scheduler (Планировщик задач)

1. Откройте Планировщик задач
2. Создать задачу → Общие
   - Имя: AI Assistant
   - Выполнять с наивысшими правами
3. Триггеры → Создать
   - При запуске
4. Действия → Создать
   - Программа: `C:\Python311\python.exe`
   - Аргументы: `D:\das\Automatition\run_ai_assistant.py`
   - Рабочая папка: `D:\das\Automatition`

### Вариант 2: Startup (Автозагрузка)

Создайте `start_ai_assistant.bat`:

```bat
@echo off
cd D:\das\Automatition
set PYTHONPATH=%CD%
set DRY_RUN_MODE=true
python run_ai_assistant.py
```

Поместите в:
```
C:\Users\YourUser\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

---

## Запуск как Windows Service

### Используя NSSM (Non-Sucking Service Manager)

1. **Скачайте NSSM:**
   ```
   https://nssm.cc/download
   ```

2. **Установите сервис:**
   ```cmd
   nssm install AIAssistant
   ```

3. **Настройте:**
   - Path: `C:\Python311\python.exe`
   - Startup directory: `D:\das\Automatition`
   - Arguments: `run_ai_assistant.py`
   - Environment:
     ```
     PYTHONPATH=D:\das\Automatition
     DRY_RUN_MODE=true
     ```

4. **Запустите:**
   ```cmd
   nssm start AIAssistant
   ```

---

## Тестирование без запуска сервера

```powershell
# Прямой тест классификатора
python test_classifier_direct.py

# Проверка всех модулей
python test_verification.py
```

---

## Логи на Windows

Логи сохраняются в:
```
D:\das\Automatition\ai_assistant.log
```

Просмотр:
```powershell
# PowerShell
Get-Content ai_assistant.log -Tail 50 -Wait

# CMD
type ai_assistant.log
```

---

## Полезные команды PowerShell

```powershell
# Проверка Python
python --version

# Проверка установленных пакетов
pip list

# Переустановка зависимостей
pip install -r ai_assistant\requirements.txt --force-reinstall

# Проверка процессов Python
Get-Process python

# Остановка всех процессов Python
Get-Process python | Stop-Process

# Проверка портов
netstat -ano | findstr :5000

# Проверка структуры проекта
tree /F ai_assistant
```

---

## Структура проекта для Windows

```
D:\das\Automatition\
├── ai_assistant\
│   ├── app\
│   │   ├── config.py           ← ДОЛЖЕН СУЩЕСТВОВАТЬ!
│   │   ├── main.py
│   │   ├── classifier.py
│   │   └── ...
│   ├── models\
│   │   └── classifier_model.pkl ← Создается при обучении
│   └── scripts\
│       └── train_model.py
├── run_ai_assistant.py
├── run_windows.bat             ← Автоматический запуск
└── config.py.example           ← Шаблон
```

---

## Готово!

После выполнения всех шагов:

✅ Сервер доступен: http://localhost:5000
✅ Health check: http://localhost:5000/health
✅ Метрики: http://localhost:5000/metrics

---

## Нужна помощь?

1. Проверьте `ai_assistant.log`
2. Убедитесь, что `ai_assistant\app\config.py` существует
3. Проверьте PYTHONPATH: `echo $env:PYTHONPATH`
4. Переустановите зависимости: `pip install -r ai_assistant\requirements.txt`
