#!/usr/bin/env python3
"""
Скрипт для комплексной проверки работоспособности кода
"""

import sys
import traceback

def test_imports():
    """Проверка импорта всех модулей"""
    print("=" * 60)
    print("ТЕСТ 1: Проверка импортов модулей")
    print("=" * 60)

    tests = []

    # Тест 1: naumen_sdk
    try:
        from naumen_sdk import NaumenClient
        print("✓ naumen_sdk.NaumenClient импортирован успешно")
        tests.append(("NaumenClient import", True))
    except Exception as e:
        print(f"✗ Ошибка импорта naumen_sdk.NaumenClient: {e}")
        tests.append(("NaumenClient import", False))

    # Тест 2: IncidentHandler
    try:
        from automation.auto_incident_handler import IncidentHandler
        print("✓ automation.auto_incident_handler.IncidentHandler импортирован успешно")
        tests.append(("IncidentHandler import", True))
    except Exception as e:
        print(f"✗ Ошибка импорта IncidentHandler: {e}")
        tests.append(("IncidentHandler import", False))

    # Тест 3: BulkOperations
    try:
        from automation.bulk_operations import BulkOperations
        print("✓ automation.bulk_operations.BulkOperations импортирован успешно")
        tests.append(("BulkOperations import", True))
    except Exception as e:
        print(f"✗ Ошибка импорта BulkOperations: {e}")
        tests.append(("BulkOperations import", False))

    # Тест 4: SLAMonitor
    try:
        from automation.sla_monitor import SLAMonitor
        print("✓ automation.sla_monitor.SLAMonitor импортирован успешно")
        tests.append(("SLAMonitor import", True))
    except Exception as e:
        print(f"✗ Ошибка импорта SLAMonitor: {e}")
        tests.append(("SLAMonitor import", False))

    return tests

def test_class_instantiation():
    """Проверка создания экземпляров классов"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Проверка создания экземпляров классов")
    print("=" * 60)

    tests = []

    # Тест создания NaumenClient
    try:
        from naumen_sdk import NaumenClient
        client = NaumenClient("https://test.example.com", "test-api-key")
        print("✓ NaumenClient создан успешно")
        tests.append(("NaumenClient instantiation", True))

        # Проверка атрибутов
        assert hasattr(client, 'base_url'), "Отсутствует атрибут base_url"
        assert hasattr(client, 'access_key'), "Отсутствует атрибут access_key"
        assert client.base_url == "https://test.example.com", "Неверный base_url"
        print("  - Атрибуты клиента проверены")

    except Exception as e:
        print(f"✗ Ошибка создания NaumenClient: {e}")
        tests.append(("NaumenClient instantiation", False))
        traceback.print_exc()

    # Тест создания IncidentHandler
    try:
        from naumen_sdk import NaumenClient
        from automation.auto_incident_handler import IncidentHandler
        client = NaumenClient("https://test.example.com", "test-api-key")
        handler = IncidentHandler(client)
        print("✓ IncidentHandler создан успешно")
        tests.append(("IncidentHandler instantiation", True))
    except Exception as e:
        print(f"✗ Ошибка создания IncidentHandler: {e}")
        tests.append(("IncidentHandler instantiation", False))
        traceback.print_exc()

    # Тест создания BulkOperations
    try:
        from naumen_sdk import NaumenClient
        from automation.bulk_operations import BulkOperations
        client = NaumenClient("https://test.example.com", "test-api-key")
        bulk_ops = BulkOperations(client)
        print("✓ BulkOperations создан успешно")
        tests.append(("BulkOperations instantiation", True))
    except Exception as e:
        print(f"✗ Ошибка создания BulkOperations: {e}")
        tests.append(("BulkOperations instantiation", False))
        traceback.print_exc()

    # Тест создания SLAMonitor
    try:
        from naumen_sdk import NaumenClient
        from automation.sla_monitor import SLAMonitor
        client = NaumenClient("https://test.example.com", "test-api-key")
        sla_monitor = SLAMonitor(client)
        print("✓ SLAMonitor создан успешно")
        tests.append(("SLAMonitor instantiation", True))
    except Exception as e:
        print(f"✗ Ошибка создания SLAMonitor: {e}")
        tests.append(("SLAMonitor instantiation", False))
        traceback.print_exc()

    return tests

def test_methods_exist():
    """Проверка наличия основных методов"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Проверка наличия методов")
    print("=" * 60)

    tests = []

    try:
        from naumen_sdk import NaumenClient
        client = NaumenClient("https://test.example.com", "test-api-key")

        required_methods = [
            'create_service_call',
            'get_service_call',
            'update_service_call',
            'close_service_call',
            'search_service_calls',
            'add_comment',
            'get_comments'
        ]

        for method in required_methods:
            if hasattr(client, method):
                print(f"✓ Метод {method} найден")
                tests.append((f"Method {method}", True))
            else:
                print(f"✗ Метод {method} не найден")
                tests.append((f"Method {method}", False))

    except Exception as e:
        print(f"✗ Ошибка при проверке методов: {e}")
        tests.append(("Methods check", False))
        traceback.print_exc()

    return tests

def test_dependencies():
    """Проверка внешних зависимостей"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Проверка зависимостей")
    print("=" * 60)

    tests = []

    # Проверка requests
    try:
        import requests
        print(f"✓ requests {requests.__version__} установлен")
        tests.append(("requests library", True))
    except ImportError:
        print("✗ requests не установлен")
        tests.append(("requests library", False))

    # Проверка urllib3
    try:
        import urllib3
        print(f"✓ urllib3 {urllib3.__version__} установлен")
        tests.append(("urllib3 library", True))
    except ImportError:
        print("✗ urllib3 не установлен")
        tests.append(("urllib3 library", False))

    return tests

def print_summary(all_tests):
    """Вывод итогового отчета"""
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)

    total = len(all_tests)
    passed = sum(1 for _, result in all_tests if result)
    failed = total - passed

    print(f"\nВсего тестов: {total}")
    print(f"Успешно: {passed} ✓")
    print(f"Неудачно: {failed} ✗")
    print(f"Процент успеха: {(passed/total*100):.1f}%")

    if failed > 0:
        print("\nПроваленные тесты:")
        for name, result in all_tests:
            if not result:
                print(f"  ✗ {name}")

    print("\n" + "=" * 60)

    return failed == 0

def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА РАБОТОСПОСОБНОСТИ КОДА")
    print("Naumen Service Desk Automation")
    print("=" * 60 + "\n")

    all_tests = []

    # Запуск всех тестов
    all_tests.extend(test_imports())
    all_tests.extend(test_class_instantiation())
    all_tests.extend(test_methods_exist())
    all_tests.extend(test_dependencies())

    # Итоговый отчет
    success = print_summary(all_tests)

    if success:
        print("\n🎉 Все проверки пройдены успешно!")
        print("Код готов к использованию.\n")
        return 0
    else:
        print("\n⚠️  Обнаружены ошибки!")
        print("Необходимо исправить проблемы перед использованием.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
