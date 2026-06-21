from __future__ import annotations

import base64
import json
from typing import Any

try:
    from .agent import invoke_calculator_agent
except ImportError:  # Lambda zip places modules at the package root.
    from agent import invoke_calculator_agent


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "content-type",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
}


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    method = (
        event.get("requestContext", {})
        .get("http", {})
        .get("method", "")
        .upper()
    )
    if method == "OPTIONS":
        return _response(204, {})

    try:
        payload = _read_payload(event)
        question = payload.get("question") or payload.get("expression")
        if not question:
            return _response(400, {"error": "Provide 'question' or 'expression'."})

        result = invoke_calculator_agent(str(question))
        status_code = 400 if "error" in result else 200
        return _response(status_code, result)
    except json.JSONDecodeError:
        return _response(400, {"error": "Request body must be valid JSON."})
    except Exception as exc:
        return _response(500, {"error": f"Unexpected error: {exc}"})


def _read_payload(event: dict[str, Any]) -> dict[str, Any]:
    if "question" in event or "expression" in event:
        return event

    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    payload = json.loads(body)
    query_params = event.get("queryStringParameters") or {}
    if query_params:
        payload = {**query_params, **payload}
    return payload


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            **CORS_HEADERS,
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }

