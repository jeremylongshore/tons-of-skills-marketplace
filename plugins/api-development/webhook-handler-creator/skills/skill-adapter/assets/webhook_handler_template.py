#!/usr/bin/env python3

"""
A basic Python template for a webhook handler with signature verification
and idempotency.  Provides a starting point for building robust and secure
webhook integrations.
"""

import hashlib
import hmac
import json
import logging
import os
import re
import time
from functools import wraps
from http import HTTPStatus
from typing import Callable, Dict

from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

_CONTROL_CHARS = re.compile(r"[\r\n\t\x00-\x1f\x7f]")


def sanitize_for_log(value) -> str:
    """
    Strips CR/LF/control characters from a user- or payload-controlled value
    before it is written to the log, preventing log-injection / forged log
    entries.

    Args:
        value: Any value destined for a log message.

    Returns:
        str: A single-line, control-character-free representation of value.
    """
    # Remove CR/LF with str.replace first (the pattern CodeQL recognizes as
    # a log-injection sanitizer), then strip the remaining control chars.
    text = str(value).replace("\r", "").replace("\n", "")
    return _CONTROL_CHARS.sub("", text)


# Environment variables (replace with your actual values)
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "your_secret_key")
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", 3))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", 1))  # Initial delay in seconds


app = Flask(__name__)


class WebhookError(Exception):
    """Base class for webhook-related exceptions."""

    pass


class SignatureVerificationError(WebhookError):
    """Raised when webhook signature verification fails."""

    pass


class IdempotencyError(WebhookError):
    """Raised when idempotency check fails."""

    pass


def verify_signature(request_data: bytes, signature: str, secret: str) -> None:
    """
    Verifies the webhook signature against the request body and secret.

    Args:
        request_data: The raw bytes of the request body.
        signature: The signature sent in the webhook request headers.
        secret: The secret key used to generate the signature.

    Raises:
        SignatureVerificationError: If the signature does not match.
    """
    try:
        expected_signature = hmac.new(secret.encode("utf-8"), request_data, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            raise SignatureVerificationError("Invalid webhook signature.")
    except Exception as e:
        logging.error(f"Signature verification failed: {e}")
        raise SignatureVerificationError("Signature verification failed.") from e


def idempotent(func: Callable) -> Callable:
    """
    Decorator to ensure idempotency of webhook requests.  This example uses a
    simple in-memory store.  For production, use a persistent database
    (e.g., Redis, PostgreSQL).

    Args:
        func: The function to decorate (webhook handler).

    Returns:
        The decorated function.

    Raises:
        IdempotencyError: If the request ID has already been processed.
    """
    processed_requests: Dict[str, bool] = {}  # In-memory store (replace in production)

    @wraps(func)
    def wrapper(*args, **kwargs):
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            logging.warning("Missing X-Request-ID header. Idempotency check skipped.")
            return func(*args, **kwargs)  # Skip idempotency check if no request ID

        if request_id in processed_requests:
            raise IdempotencyError(f"Request with ID {request_id} already processed.")

        try:
            result = func(*args, **kwargs)
            processed_requests[request_id] = True  # Mark as processed
            return result
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            raise

    return wrapper


def retry(func: Callable, max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY) -> Callable:
    """
    Decorator to add retry logic with exponential backoff.

    Args:
        func: The function to decorate.
        max_retries: The maximum number of retries.
        delay: The initial delay in seconds.

    Returns:
        The decorated function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal delay
        attempts = 0
        while attempts < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                logging.warning(f"Attempt {attempts} failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        logging.error(f"Max retries reached. Function {func.__name__} failed.")
        raise

    return wrapper


@app.route("/webhook", methods=["POST"])
@idempotent
@retry
def handle_webhook():
    """
    Handles incoming webhook requests.

    This function verifies the signature, processes the event, and returns a
    success response.  It also includes error handling and retry logic.
    """
    signature = request.headers.get("X-Webhook-Signature")
    if not signature:
        logging.warning("Missing X-Webhook-Signature header.")
        return jsonify({"error": "Missing signature"}), HTTPStatus.BAD_REQUEST

    request_data = request.get_data()

    try:
        verify_signature(request_data, signature, WEBHOOK_SECRET)
    except SignatureVerificationError:
        logging.warning("Signature verification failed")
        return jsonify({"error": "Signature verification failed"}), HTTPStatus.UNAUTHORIZED

    try:
        payload = json.loads(request_data.decode("utf-8"))
        event_type = payload.get("type")  # Example: Get event type from payload

        # Route the event to the appropriate handler (replace with your logic)
        if event_type == "user.created":
            process_user_created_event(payload)
        elif event_type == "payment.succeeded":
            process_payment_succeeded_event(payload)
        else:
            logging.warning(f"Unhandled event type: {sanitize_for_log(event_type)}")
            return jsonify({"status": "unhandled"}), HTTPStatus.OK  # Acknowledge the event

        return jsonify({"status": "success"}), HTTPStatus.OK

    except json.JSONDecodeError:
        logging.error("Invalid JSON payload")
        return jsonify({"error": "Invalid JSON payload"}), HTTPStatus.BAD_REQUEST
    except Exception:
        logging.exception("Error processing webhook")
        return jsonify({"error": "Internal server error"}), HTTPStatus.INTERNAL_SERVER_ERROR


def process_user_created_event(payload: Dict) -> None:
    """
    Processes a user.created event.  This is a placeholder; replace with
    your actual business logic.

    Args:
        payload: The event payload as a dictionary.
    """
    user_id = payload.get("user_id")
    logging.info(f"Processing user.created event for user ID: {sanitize_for_log(user_id)}")
    # Add your business logic here (e.g., create user in your system)
    time.sleep(0.1)  # Simulate some processing time


def process_payment_succeeded_event(payload: Dict) -> None:
    """
    Processes a payment.succeeded event. This is a placeholder; replace with
    your actual business logic.

    Args:
        payload: The event payload as a dictionary.
    """
    payment_id = payload.get("payment_id")
    logging.info(f"Processing payment.succeeded event for payment ID: {sanitize_for_log(payment_id)}")
    # Add your business logic here (e.g., update order status)
    time.sleep(0.2)  # Simulate some processing time


@app.errorhandler(SignatureVerificationError)
def handle_signature_error(error):
    """Handles SignatureVerificationError exceptions."""
    return jsonify({"error": str(error)}), HTTPStatus.UNAUTHORIZED


@app.errorhandler(IdempotencyError)
def handle_idempotency_error(error):
    """Handles IdempotencyError exceptions."""
    return jsonify({"error": str(error)}), HTTPStatus.CONFLICT


@app.errorhandler(Exception)
def handle_generic_error(error):
    """Handles generic exceptions."""
    logging.exception("Unhandled exception")
    return jsonify({"error": "Internal server error"}), HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    # Example Usage:
    #
    # 1. Set the WEBHOOK_SECRET environment variable.
    # 2. Run the Flask app: python webhook_handler_template.py
    # 3. Send a POST request to /webhook with a valid X-Webhook-Signature header.
    #
    # Example request:
    #
    # POST /webhook HTTP/1.1
    # X-Webhook-Signature: <calculated_signature>
    # X-Request-ID: <unique_request_id>
    # Content-Type: application/json
    #
    # {
    #   "type": "user.created",
    #   "user_id": "123"
    # }

    # Debug mode is opt-in only (never default-on): the Flask debugger exposes
    # an interactive Werkzeug console that allows arbitrary code execution if
    # reachable. Set WEBHOOK_DEBUG=1 for local development only; never enable
    # it while bound to 0.0.0.0 or in production.
    debug_mode = os.environ.get("WEBHOOK_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
