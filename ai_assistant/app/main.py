"""
Flask API для AI Assistant
"""
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

from ai_assistant.app.config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, AUTO_APPLY_THRESHOLD
from ai_assistant.app.classifier import get_classifier
from ai_assistant.app.naumen_integration import get_naumen_integration
from ai_assistant.app.utils.logger import logger, log_classification, log_error
from ai_assistant.app.utils.metrics import (
    MetricsCollector,
    metrics_endpoint
)

# Создание Flask приложения
app = Flask(__name__)
CORS(app)  # Разрешаем CORS для интеграции

# Инициализация компонентов
classifier = get_classifier()
naumen = get_naumen_integration()
metrics = MetricsCollector()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ai-assistant",
        "version": "1.0.0"
    }), 200


@app.route('/metrics', methods=['GET'])
def metrics_handler():
    """Prometheus metrics endpoint"""
    return metrics_endpoint()


@app.route('/ai/classify', methods=['POST'])
def classify_ticket():
    """
    Endpoint для классификации заявки

    Ожидает JSON:
    {
        "ticket_id": "INC-2025-0001",
        "subject": "Не работает Outlook",
        "description": "Outlook при запуске выдает ошибку и закрывается"
    }

    Возвращает:
    {
        "ticket_id": "INC-2025-0001",
        "classification": {
            "category": "Почта",
            "support_group": "1 линия",
            "priority": "Normal",
            "confidence": 0.85,
            "method": "rule_based"
        },
        "action": "auto_apply",
        "applied": true,
        "processing_time_ms": 123.45
    }
    """
    start_time = time.time()
    metrics.increment_active_requests()

    try:
        # Валидация запроса
        data = request.get_json()
        if not data:
            metrics.decrement_active_requests()
            metrics.record_error("invalid_request")
            return jsonify({"error": "Invalid JSON"}), 400

        ticket_id = data.get('ticket_id')
        subject = data.get('subject', '')
        description = data.get('description', '')

        if not ticket_id or not subject:
            metrics.decrement_active_requests()
            metrics.record_error("missing_fields")
            return jsonify({"error": "ticket_id and subject are required"}), 400

        logger.info(f"Processing classification request for ticket {ticket_id}")

        # Классификация
        classification = classifier.classify(subject, description)
        confidence = classification['confidence']

        # Определение действия
        suggested_action = classifier.get_suggested_action(confidence)

        # Применение результата
        applied = False
        if suggested_action == "auto_apply":
            # Автоматически применяем изменения
            applied = naumen.update_ticket(ticket_id, classification)
            if applied:
                metrics.record_auto_applied(classification['category'])
        elif suggested_action == "suggest":
            # Добавляем комментарий с рекомендацией
            naumen.add_suggestion_comment(ticket_id, classification)

        # Время обработки
        processing_time = time.time() - start_time

        # Метрики
        metrics.record_request("success")
        metrics.record_processing_time(processing_time)
        metrics.record_confidence(confidence)

        # Логирование
        log_classification(
            ticket_id, subject, classification,
            confidence, processing_time, applied
        )

        # Ответ
        response = {
            "ticket_id": ticket_id,
            "classification": classification,
            "action": suggested_action,
            "applied": applied,
            "processing_time_ms": round(processing_time * 1000, 2)
        }

        metrics.decrement_active_requests()
        return jsonify(response), 200

    except Exception as e:
        processing_time = time.time() - start_time
        metrics.decrement_active_requests()
        metrics.record_request("error")
        metrics.record_error("internal_error")

        ticket_id = data.get('ticket_id', 'unknown') if data else 'unknown'
        log_error(ticket_id, str(e), "internal_error")

        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/naumen/webhook', methods=['POST'])
def naumen_webhook():
    """
    Webhook endpoint для получения событий от Naumen

    Ожидает JSON:
    {
        "event": "ticket_created",
        "ticket": {
            "id": "INC-2025-0001",
            "subject": "...",
            "description": "...",
            ...
        }
    }
    """
    start_time = time.time()

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        event = data.get('event')
        ticket = data.get('ticket', {})

        logger.info(f"Received webhook event: {event}")

        # Обрабатываем только создание заявок
        if event == "ticket_created":
            ticket_id = ticket.get('id')
            subject = ticket.get('subject', '')
            description = ticket.get('description', '')

            if not ticket_id or not subject:
                return jsonify({"error": "Missing ticket data"}), 400

            # Классификация
            classification = classifier.classify(subject, description)
            confidence = classification['confidence']
            suggested_action = classifier.get_suggested_action(confidence)

            # Применение
            applied = False
            if suggested_action == "auto_apply":
                applied = naumen.update_ticket(ticket_id, classification)
                if applied:
                    metrics.record_auto_applied(classification['category'])
            elif suggested_action == "suggest":
                naumen.add_suggestion_comment(ticket_id, classification)

            processing_time = time.time() - start_time
            metrics.record_request("success")
            metrics.record_processing_time(processing_time)
            metrics.record_confidence(confidence)

            log_classification(
                ticket_id, subject, classification,
                confidence, processing_time, applied
            )

            return jsonify({
                "status": "processed",
                "ticket_id": ticket_id,
                "action": suggested_action,
                "applied": applied
            }), 200

        return jsonify({"status": "ignored", "event": event}), 200

    except Exception as e:
        metrics.record_request("error")
        metrics.record_error("webhook_error")
        logger.error(f"Webhook processing error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/batch/classify', methods=['POST'])
def batch_classify():
    """
    Batch endpoint для классификации множества заявок

    Ожидает JSON:
    {
        "tickets": [
            {"ticket_id": "...", "subject": "...", "description": "..."},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        tickets = data.get('tickets', [])

        if not tickets:
            return jsonify({"error": "No tickets provided"}), 400

        results = []
        for ticket_data in tickets:
            ticket_id = ticket_data.get('ticket_id')
            subject = ticket_data.get('subject', '')
            description = ticket_data.get('description', '')

            if not ticket_id or not subject:
                continue

            classification = classifier.classify(subject, description)
            results.append({
                "ticket_id": ticket_id,
                "classification": classification
            })

        return jsonify({
            "processed": len(results),
            "results": results
        }), 200

    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        return jsonify({"error": str(e)}), 500


def main():
    """Запуск Flask приложения"""
    logger.info(f"Starting AI Assistant on {FLASK_HOST}:{FLASK_PORT}")
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )


if __name__ == "__main__":
    main()
