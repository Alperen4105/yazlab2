from typing import Any, Dict, Optional, Tuple

from flask import current_app


def call_api(
    method: str,
    path: str,
    *,
    json: Optional[Dict[str, Any]] = None,
    query_string: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Tuple[Optional[Dict[str, Any]], int]:
    """Invoke the internal API blueprint via Flask's test client."""

    with current_app.test_client() as client:
        http_method = getattr(client, method.lower())
        response = http_method(
            path,
            json=json,
            query_string=query_string,
            headers=headers,
        )
        data = None
        if response.is_json:
            data = response.get_json()
        return data, response.status_code

