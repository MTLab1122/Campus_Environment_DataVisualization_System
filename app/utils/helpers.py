"""
General helper utilities for JSON responses, parsing, and formatting.
"""
from datetime import datetime, timezone
from typing import Any, Optional, Tuple, Dict
from flask import jsonify, Response


def utc_now() -> datetime:
    """Return timezone-naive UTC datetime for consistent storage and comparisons."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def api_response(data: Any = None, message: str = "Success", status_code: int = 200) -> Tuple[Response, int]:
    """Uniform JSON API success response format."""
    payload = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(payload), status_code


def api_error(message: str = "An error occurred", status_code: int = 400, errors: Any = None) -> Tuple[Response, int]:
    """Uniform JSON API error response format."""
    payload = {
        "success": False,
        "message": message,
        "errors": errors or []
    }
    return jsonify(payload), status_code


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Safely parse ISO or standard date/datetime strings."""
    if not dt_str:
        return None
    dt_str = dt_str.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    try:
        # Fallback to fromisoformat
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None
