# Инструкция по развертыванию AI Assistant на сервере

## Вариант 1: Через Git (Рекомендуется)

### Шаг 1: Подключитесь к серверу

```bash
ssh user@your-server.com
```

### Шаг 2: Клонируйте репозиторий

```bash
# Клонирование репозитория
git clone https://github.com/ATOMEXXX0526/Automatition.git
cd Automatition

# Переключитесь на нужную ветку (или создайте merge в main)
git checkout claude/investigate-issue-011CUKxLuSNSKX9d4dXXPWJJ
```

### Шаг 3: Установите зависимости

```bash
# Установка Python зависимостей
cd ai_assistant
pip3 install -r requirements.txt

# Или с виртуальным окружением (рекомендуется)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 4: Настройте конфигурацию

```bash
# Создайте файл конфигурации
cp .env.example .env

# Отредактируйте настройки
nano .env
```

Заполните `.env`:
```bash
# Naumen Service Desk
NAUMEN_URL=https://your-naumen-server.com
NAUMEN_API_KEY=your-api-key-here
NAUMEN_VERIFY_SSL=true

# AI настройки
AUTO_APPLY_THRESHOLD=0.80
MIN_CONFIDENCE_THRESHOLD=0.50

# Режим работы
DRY_RUN_MODE=true  # Сначала true для тестирования!

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Логирование
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Шаг 5: Обучите модель

```bash
# Обучение на тестовых данных
python3 scripts/train_model.py

# Или используйте свои данные
# 1. Положите данные в data/training_data.json
# 2. Запустите обучение
```

### Шаг 6: Запустите сервис

#### Вариант А: Простой запуск (для тестирования)

```bash
cd ..
export PYTHONPATH=/path/to/Automatition
python3 run_ai_assistant.py
```

#### Вариант Б: С systemd (Production)

Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/ai-assistant.service
```

Содержимое:
```ini
[Unit]
Description=AI Assistant for Naumen Service Desk
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Automatition
Environment="PYTHONPATH=/path/to/Automatition"
Environment="DRY_RUN_MODE=true"
ExecStart=/usr/bin/python3 /path/to/Automatition/run_ai_assistant.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-assistant
sudo systemctl start ai-assistant
sudo systemctl status ai-assistant
```

Логи:
```bash
sudo journalctl -u ai-assistant -f
```

#### Вариант В: С supervisor

```bash
sudo apt-get install supervisor

sudo nano /etc/supervisor/conf.d/ai-assistant.conf
```

Содержимое:
```ini
[program:ai-assistant]
command=/usr/bin/python3 /path/to/Automatition/run_ai_assistant.py
directory=/path/to/Automatition
environment=PYTHONPATH="/path/to/Automatition",DRY_RUN_MODE="true"
user=your-user
autostart=true
autorestart=true
stderr_logfile=/var/log/ai-assistant.err.log
stdout_logfile=/var/log/ai-assistant.out.log
```

Запуск:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-assistant
sudo supervisorctl status
```

### Шаг 7: Настройте Nginx (опционально, для production)

```bash
sudo nano /etc/nginx/sites-available/ai-assistant
```

Содержимое:
```nginx
server {
    listen 80;
    server_name ai-assistant.your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:
```bash
sudo ln -s /etc/nginx/sites-available/ai-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Шаг 8: Проверьте работу

```bash
# Health check
curl http://localhost:5000/health

# Тест классификации
curl -X POST http://localhost:5000/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "subject": "Не работает Outlook",
    "description": "Ошибка при запуске"
  }'

# Метрики
curl http://localhost:5000/metrics
```

---

## Вариант 2: Через SCP/SFTP (если нет git на сервере)

### Шаг 1: Упакуйте проект локально

```bash
# На вашей локальной машине
cd /home/user/Automatition
tar -czf ai-assistant.tar.gz \
    ai_assistant/ \
    naumen_sdk/ \
    automation/ \
    run_ai_assistant.py \
    test_classifier_direct.py \
    test_verification.py \
    config.py.example \
    requirements.txt \
    README.md

# Проверка архива
ls -lh ai-assistant.tar.gz
```

### Шаг 2: Загрузите на сервер

```bash
# Через SCP
scp ai-assistant.tar.gz user@your-server.com:/home/user/

# Или через SFTP
sftp user@your-server.com
put ai-assistant.tar.gz
exit
```

### Шаг 3: Распакуйте на сервере

```bash
# Подключитесь к серверу
ssh user@your-server.com

# Создайте директорию
mkdir -p /opt/ai-assistant
cd /opt/ai-assistant

# Распакуйте
tar -xzf ~/ai-assistant.tar.gz

# Дальше следуйте шагам 3-8 из Варианта 1
```

---

## Вариант 3: Через Docker (если поддерживается)

Если на сервере есть Docker, можно создать простой Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копируем проект
COPY . /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r ai_assistant/requirements.txt

# Обучаем модель
RUN python3 ai_assistant/scripts/train_model.py

# Переменные окружения
ENV PYTHONPATH=/app
ENV DRY_RUN_MODE=true

# Порт
EXPOSE 5000

# Запуск
CMD ["python3", "run_ai_assistant.py"]
```

Сборка и запуск:
```bash
# Сборка
docker build -t ai-assistant .

# Запуск
docker run -d \
  --name ai-assistant \
  -p 5000:5000 \
  -e NAUMEN_URL=https://your-naumen.com \
  -e NAUMEN_API_KEY=your-key \
  -v $(pwd)/ai_assistant/logs:/app/ai_assistant/logs \
  ai-assistant

# Логи
docker logs -f ai-assistant
```

---

## Важные замечания

### 🔒 Безопасность

1. **API ключи** - храните в переменных окружения, НЕ в коде
2. **Firewall** - откройте только нужные порты
   ```bash
   sudo ufw allow 5000/tcp
   sudo ufw enable
   ```
3. **SSL** - используйте HTTPS в production (Let's Encrypt)
4. **DRY_RUN** - начните с режима тестирования

### 📊 Мониторинг

```bash
# Проверка работы сервиса
systemctl status ai-assistant

# Логи
tail -f /var/log/ai-assistant.out.log
tail -f ai_assistant/ai_assistant.log

# Метрики
curl http://localhost:5000/metrics
```

### 🔄 Обновление

```bash
# Через Git
cd /path/to/Automatition
git pull origin claude/investigate-issue-011CUKxLuSNSKX9d4dXXPWJJ
sudo systemctl restart ai-assistant

# Через SCP
# Загрузите новый архив и распакуйте
sudo systemctl restart ai-assistant
```

---

## Быстрая проверка после развертывания

```bash
#!/bin/bash
# Скрипт проверки (сохраните как check_deployment.sh)

echo "Проверка AI Assistant..."

# 1. Health check
echo "1. Health check..."
curl -s http://localhost:5000/health | python3 -m json.tool

# 2. Тест классификации
echo -e "\n2. Тест классификации..."
curl -s -X POST http://localhost:5000/ai/classify \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"TEST-001","subject":"Принтер не работает","description":"HP не печатает"}' \
  | python3 -m json.tool

# 3. Проверка процесса
echo -e "\n3. Проверка процесса..."
ps aux | grep ai_assistant

# 4. Проверка портов
echo -e "\n4. Проверка портов..."
sudo netstat -tulpn | grep 5000

echo -e "\n✅ Проверка завершена!"
```

Запуск:
```bash
chmod +x check_deployment.sh
./check_deployment.sh
```

---

## Troubleshooting

### Проблема: ModuleNotFoundError

```bash
# Решение: установите PYTHONPATH
export PYTHONPATH=/path/to/Automatition
# Или добавьте в .bashrc
echo 'export PYTHONPATH=/path/to/Automatition' >> ~/.bashrc
```

### Проблема: Порт занят

```bash
# Найти процесс
sudo lsof -i :5000

# Убить процесс
sudo kill -9 <PID>

# Или изменить порт
export FLASK_PORT=5001
```

### Проблема: Модель не найдена

```bash
# Обучите модель
cd /path/to/Automatition
python3 ai_assistant/scripts/train_model.py
```

---

Какой вариант развертывания вам подходит? Могу помочь с настройкой!
