"""
ML классификатор заявок на базе TF-IDF
"""
import re
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pymorphy2

from app.config import (
    MODEL_PATH,
    VECTORIZER_PATH,
    CATEGORIES,
    SUPPORT_GROUPS,
    PRIORITIES,
    CATEGORY_TO_GROUP_MAPPING,
    MIN_CONFIDENCE_THRESHOLD
)
from app.utils.logger import logger


class TextPreprocessor:
    """Предобработка русского текста"""

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def preprocess(self, text: str) -> str:
        """
        Предобработка текста

        Args:
            text: Исходный текст

        Returns:
            Обработанный текст
        """
        if not text:
            return ""

        # Приведение к нижнему регистру
        text = text.lower()

        # Удаление спецсимволов (оставляем буквы и пробелы)
        text = re.sub(r'[^а-яёa-z\s]', ' ', text)

        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text).strip()

        # Лемматизация (приведение к базовой форме)
        words = text.split()
        lemmas = []
        for word in words:
            if len(word) > 2:  # Пропускаем короткие слова
                parsed = self.morph.parse(word)[0]
                lemmas.append(parsed.normal_form)

        return ' '.join(lemmas)


class TicketClassifier:
    """Классификатор заявок"""

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.category_model: Optional[Pipeline] = None
        self.priority_model: Optional[Pipeline] = None
        self.loaded = False

    def load_models(self):
        """Загрузка обученных моделей"""
        try:
            if MODEL_PATH.exists():
                models_data = joblib.load(MODEL_PATH)
                self.category_model = models_data.get('category_model')
                self.priority_model = models_data.get('priority_model')
                self.loaded = True
                logger.info(f"Models loaded successfully from {MODEL_PATH}")
            else:
                logger.warning(f"Model file not found: {MODEL_PATH}. Using rule-based classification.")
                self.loaded = False
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.loaded = False

    def _rule_based_classification(self, text: str) -> Tuple[str, str, str, float]:
        """
        Классификация на основе правил (fallback)

        Args:
            text: Предобработанный текст

        Returns:
            (категория, группа, приоритет, confidence)
        """
        text_lower = text.lower()

        # Определение категории по ключевым словам
        category = "Прочее"
        confidence = 0.6

        if any(word in text_lower for word in ['почта', 'outlook', 'email', 'письмо', 'mail']):
            category = "Почта"
            confidence = 0.75
        elif any(word in text_lower for word in ['сеть', 'интернет', 'wifi', 'vpn', 'подключение']):
            category = "Сеть"
            confidence = 0.75
        elif any(word in text_lower for word in ['1c', 'бухгалтерия', 'зуп', 'erp']):
            category = "1C"
            confidence = 0.75
        elif any(word in text_lower for word in ['принтер', 'сканер', 'мфу', 'монитор', 'клавиатура']):
            category = "Оборудование"
            confidence = 0.75
        elif any(word in text_lower for word in ['доступ', 'пароль', 'права', 'логин', 'учетная запись']):
            category = "Доступ"
            confidence = 0.75

        # Определение приоритета
        priority = "Normal"
        if any(word in text_lower for word in ['критично', 'срочно', 'critical', 'все', 'полностью']):
            priority = "High"
            confidence = min(confidence + 0.05, 0.95)
        elif any(word in text_lower for word in ['не срочно', 'когда будет время', 'low']):
            priority = "Low"

        # Определение группы поддержки
        support_group = CATEGORY_TO_GROUP_MAPPING.get(category, "1 линия")

        return category, support_group, priority, confidence

    def classify(self, subject: str, description: str = "") -> Dict:
        """
        Классификация заявки

        Args:
            subject: Тема заявки
            description: Описание заявки

        Returns:
            Словарь с результатами классификации
        """
        # Объединяем тему и описание
        combined_text = f"{subject} {description}".strip()

        # Предобработка
        processed_text = self.preprocessor.preprocess(combined_text)

        if not processed_text:
            logger.warning("Empty text after preprocessing")
            return {
                "category": "Прочее",
                "support_group": "1 линия",
                "priority": "Normal",
                "confidence": 0.5,
                "method": "default"
            }

        # Если модель загружена, используем её
        if self.loaded and self.category_model:
            try:
                # Предсказание категории
                category_proba = self.category_model.predict_proba([processed_text])[0]
                category_idx = np.argmax(category_proba)
                category = self.category_model.classes_[category_idx]
                confidence = float(category_proba[category_idx])

                # Предсказание приоритета
                if self.priority_model:
                    priority_proba = self.priority_model.predict_proba([processed_text])[0]
                    priority_idx = np.argmax(priority_proba)
                    priority = self.priority_model.classes_[priority_idx]
                else:
                    priority = "Normal"

                # Определение группы поддержки
                support_group = CATEGORY_TO_GROUP_MAPPING.get(category, "1 линия")

                return {
                    "category": category,
                    "support_group": support_group,
                    "priority": priority,
                    "confidence": confidence,
                    "method": "ml_model"
                }

            except Exception as e:
                logger.error(f"Error during ML classification: {e}")
                # Fallback на правила
                pass

        # Используем классификацию на основе правил
        category, support_group, priority, confidence = self._rule_based_classification(processed_text)

        return {
            "category": category,
            "support_group": support_group,
            "priority": priority,
            "confidence": confidence,
            "method": "rule_based"
        }

    def get_suggested_action(self, confidence: float) -> str:
        """
        Определение рекомендуемого действия

        Args:
            confidence: Уверенность классификатора

        Returns:
            Действие: auto_apply, suggest, manual
        """
        from app.config import AUTO_APPLY_THRESHOLD

        if confidence >= AUTO_APPLY_THRESHOLD:
            return "auto_apply"
        elif confidence >= MIN_CONFIDENCE_THRESHOLD:
            return "suggest"
        else:
            return "manual"


# Singleton instance
_classifier_instance = None


def get_classifier() -> TicketClassifier:
    """
    Получить экземпляр классификатора (singleton)

    Returns:
        TicketClassifier
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TicketClassifier()
        _classifier_instance.load_models()
    return _classifier_instance
