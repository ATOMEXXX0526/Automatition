@echo off
REM Скрипт запуска AI Assistant для Windows

echo ========================================
echo AI Assistant - Запуск на Windows
echo ========================================
echo.

REM Проверка наличия модели
if not exist "ai_assistant\models\classifier_model.pkl" (
    echo Модель не найдена. Запускаем обучение...
    python ai_assistant\scripts\train_model.py
    if errorlevel 1 (
        echo Ошибка при обучении модели!
        pause
        exit /b 1
    )
)

REM Установка переменных окружения
set PYTHONPATH=%CD%
set DRY_RUN_MODE=true
set FLASK_DEBUG=false
set LOG_FORMAT=text

echo Запуск AI Assistant...
echo PYTHONPATH=%PYTHONPATH%
echo DRY_RUN_MODE=%DRY_RUN_MODE%
echo.

REM Запуск
python run_ai_assistant.py

pause
