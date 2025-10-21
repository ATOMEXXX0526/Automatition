"""
Метрики Prometheus для AI Assistant
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
from ai_assistant.app.config import METRICS_ENABLED

# Счетчики
requests_total = Counter(
    'ai_assistant_requests_total',
    'Total number of classification requests',
    ['status']  # success, error
)

auto_applied_total = Counter(
    'ai_assistant_auto_applied_total',
    'Total number of auto-applied classifications',
    ['category']
)

errors_total = Counter(
    'ai_assistant_errors_total',
    'Total number of errors',
    ['error_type']
)

# Гистограммы
processing_latency = Histogram(
    'ai_assistant_processing_latency_seconds',
    'Time spent processing classification request',
    buckets=[0.1, 0.25, 0.5, 0.75, 1.0, 2.0, 5.0]
)

model_confidence = Histogram(
    'ai_assistant_model_confidence',
    'Model confidence score distribution',
    buckets=[0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
)

# Gauges
last_processing_time = Gauge(
    'ai_assistant_last_processing_time_seconds',
    'Last request processing time'
)

active_requests = Gauge(
    'ai_assistant_active_requests',
    'Number of requests currently being processed'
)


class MetricsCollector:
    """Класс для сбора метрик"""

    @staticmethod
    def record_request(status: str = "success"):
        """Записать запрос"""
        if METRICS_ENABLED:
            requests_total.labels(status=status).inc()

    @staticmethod
    def record_auto_applied(category: str):
        """Записать автоприменение"""
        if METRICS_ENABLED:
            auto_applied_total.labels(category=category).inc()

    @staticmethod
    def record_error(error_type: str):
        """Записать ошибку"""
        if METRICS_ENABLED:
            errors_total.labels(error_type=error_type).inc()

    @staticmethod
    def record_processing_time(duration: float):
        """Записать время обработки"""
        if METRICS_ENABLED:
            processing_latency.observe(duration)
            last_processing_time.set(duration)

    @staticmethod
    def record_confidence(confidence: float):
        """Записать уверенность модели"""
        if METRICS_ENABLED:
            model_confidence.observe(confidence)

    @staticmethod
    def increment_active_requests():
        """Увеличить счетчик активных запросов"""
        if METRICS_ENABLED:
            active_requests.inc()

    @staticmethod
    def decrement_active_requests():
        """Уменьшить счетчик активных запросов"""
        if METRICS_ENABLED:
            active_requests.dec()


def metrics_endpoint():
    """
    Endpoint для экспорта метрик Prometheus

    Returns:
        Response с метриками
    """
    if not METRICS_ENABLED:
        return Response("Metrics disabled", status=503)

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
