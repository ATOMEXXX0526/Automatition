"""
Тесты для классификатора
"""
import sys
from pathlib import Path

# Добавляем родительскую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app.classifier import TextPreprocessor, TicketClassifier


class TestTextPreprocessor:
    """Тесты предобработки текста"""

    def setup_method(self):
        self.preprocessor = TextPreprocessor()

    def test_lowercase(self):
        """Тест приведения к нижнему регистру"""
        text = "Не Работает ПРИНТЕР"
        result = self.preprocessor.preprocess(text)
        assert result.islower()

    def test_special_chars_removal(self):
        """Тест удаления спецсимволов"""
        text = "Не работает! @#$% принтер???"
        result = self.preprocessor.preprocess(text)
        assert '@' not in result
        assert '!' not in result
        assert '?' not in result

    def test_lemmatization(self):
        """Тест лемматизации"""
        text = "работает работал работающий"
        result = self.preprocessor.preprocess(text)
        # Все должны привестись к базовой форме "работать"
        assert 'работать' in result


class TestTicketClassifier:
    """Тесты классификатора"""

    def setup_method(self):
        self.classifier = TicketClassifier()

    def test_email_classification(self):
        """Тест классификации почтовых проблем"""
        result = self.classifier.classify(
            subject="Не работает Outlook",
            description="Outlook при запуске выдает ошибку"
        )

        assert result['category'] == 'Почта'
        assert result['confidence'] > 0.5

    def test_network_classification(self):
        """Тест классификации сетевых проблем"""
        result = self.classifier.classify(
            subject="Нет интернета",
            description="Не могу подключиться к сети"
        )

        assert result['category'] == 'Сеть'
        assert result['confidence'] > 0.5

    def test_1c_classification(self):
        """Тест классификации проблем с 1С"""
        result = self.classifier.classify(
            subject="Ошибка в 1С",
            description="1С Бухгалтерия не открывается"
        )

        assert result['category'] == '1C'
        assert result['confidence'] > 0.5

    def test_equipment_classification(self):
        """Тест классификации проблем с оборудованием"""
        result = self.classifier.classify(
            subject="Принтер не печатает",
            description="Принтер не отвечает на команды печати"
        )

        assert result['category'] == 'Оборудование'
        assert result['confidence'] > 0.5

    def test_access_classification(self):
        """Тест классификации проблем с доступом"""
        result = self.classifier.classify(
            subject="Забыл пароль",
            description="Не могу войти в систему, забыл пароль"
        )

        assert result['category'] == 'Доступ'
        assert result['confidence'] > 0.5

    def test_high_priority_detection(self):
        """Тест определения высокого приоритета"""
        result = self.classifier.classify(
            subject="КРИТИЧНО! Сервер недоступен",
            description="Все базы данных не работают, срочно нужна помощь"
        )

        assert result['priority'] == 'High'

    def test_empty_text(self):
        """Тест обработки пустого текста"""
        result = self.classifier.classify(
            subject="",
            description=""
        )

        assert result['category'] == 'Прочее'
        assert result['confidence'] >= 0.5

    def test_suggested_action_auto_apply(self):
        """Тест определения автоприменения при высокой уверенности"""
        # Симулируем высокую уверенность
        action = self.classifier.get_suggested_action(0.85)
        assert action == "auto_apply"

    def test_suggested_action_suggest(self):
        """Тест определения рекомендации при средней уверенности"""
        action = self.classifier.get_suggested_action(0.65)
        assert action == "suggest"

    def test_suggested_action_manual(self):
        """Тест определения ручной обработки при низкой уверенности"""
        action = self.classifier.get_suggested_action(0.45)
        assert action == "manual"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
