#!/usr/bin/env python3
"""
Скрипт обучения TF-IDF модели классификации заявок
"""
import json
import sys
from pathlib import Path

# Добавляем родительскую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

from ai_assistant.app.classifier import TextPreprocessor
from ai_assistant.app.config import MODELS_DIR, DATA_DIR


def load_training_data():
    """
    Загрузка тренировочных данных

    Returns:
        DataFrame с данными
    """
    sample_file = DATA_DIR / "sample_tickets.json"

    if not sample_file.exists():
        print(f"Sample data file not found: {sample_file}")
        sys.exit(1)

    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} training samples")
    return df


def train_category_model(df: pd.DataFrame, preprocessor: TextPreprocessor):
    """
    Обучение модели классификации категорий

    Args:
        df: DataFrame с данными
        preprocessor: Препроцессор текста

    Returns:
        Обученная модель
    """
    print("\n" + "=" * 60)
    print("Training Category Classification Model")
    print("=" * 60)

    # Предобработка текста
    df['text'] = df.apply(lambda row: f"{row['subject']} {row['description']}", axis=1)
    df['processed_text'] = df['text'].apply(preprocessor.preprocess)

    X = df['processed_text']
    y = df['category']

    # Разделение на train/test (без stratify из-за малого количества данных)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Создание pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            min_df=1
        )),
        ('classifier', LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        ))
    ])

    # Обучение
    print("Training...")
    model.fit(X_train, y_train)

    # Оценка
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\nAccuracy on test set: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=3, scoring='accuracy')
    print(f"\nCross-validation scores: {cv_scores}")
    print(f"Average CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")

    return model


def train_priority_model(df: pd.DataFrame, preprocessor: TextPreprocessor):
    """
    Обучение модели классификации приоритетов

    Args:
        df: DataFrame с данными
        preprocessor: Препроцессор текста

    Returns:
        Обученная модель
    """
    print("\n" + "=" * 60)
    print("Training Priority Classification Model")
    print("=" * 60)

    df['text'] = df.apply(lambda row: f"{row['subject']} {row['description']}", axis=1)
    df['processed_text'] = df['text'].apply(preprocessor.preprocess)

    X = df['processed_text']
    y = df['priority']

    # Разделение на train/test (без stratify из-за малого количества данных)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Создание pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            min_df=1
        )),
        ('classifier', LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        ))
    ])

    # Обучение
    print("Training...")
    model.fit(X_train, y_train)

    # Оценка
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\nAccuracy on test set: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    return model


def save_models(category_model, priority_model):
    """
    Сохранение моделей

    Args:
        category_model: Модель классификации категорий
        priority_model: Модель классификации приоритетов
    """
    # Создаем директорию для моделей
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODELS_DIR / "classifier_model.pkl"

    models_data = {
        'category_model': category_model,
        'priority_model': priority_model
    }

    joblib.dump(models_data, model_path)
    print(f"\nModels saved to {model_path}")


def test_predictions(category_model, priority_model, preprocessor):
    """
    Тестирование предсказаний на примерах

    Args:
        category_model: Модель категорий
        priority_model: Модель приоритетов
        preprocessor: Препроцессор
    """
    print("\n" + "=" * 60)
    print("Testing Predictions")
    print("=" * 60)

    test_cases = [
        "Не работает принтер в офисе",
        "Критическая проблема с базой данных 1С",
        "Не могу подключиться к VPN",
        "Нужно сбросить пароль",
        "Outlook не открывается, пишет ошибку"
    ]

    for text in test_cases:
        processed = preprocessor.preprocess(text)

        cat_proba = category_model.predict_proba([processed])[0]
        cat_idx = cat_proba.argmax()
        category = category_model.classes_[cat_idx]
        cat_conf = cat_proba[cat_idx]

        prio_proba = priority_model.predict_proba([processed])[0]
        prio_idx = prio_proba.argmax()
        priority = priority_model.classes_[prio_idx]

        print(f"\nText: {text}")
        print(f"  Category: {category} (confidence: {cat_conf:.2%})")
        print(f"  Priority: {priority}")


def main():
    """Главная функция"""
    print("AI Assistant - Model Training Script")
    print("=" * 60)

    # Загрузка данных
    df = load_training_data()

    # Инициализация препроцессора
    preprocessor = TextPreprocessor()

    # Обучение моделей
    category_model = train_category_model(df, preprocessor)
    priority_model = train_priority_model(df, preprocessor)

    # Сохранение моделей
    save_models(category_model, priority_model)

    # Тестирование
    test_predictions(category_model, priority_model, preprocessor)

    print("\n" + "=" * 60)
    print("Training completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
