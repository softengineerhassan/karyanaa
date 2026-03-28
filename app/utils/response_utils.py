
from typing import Any, Optional, Dict


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Optional[Dict[str, Any]] = None
):
    response = {
        "success": True,
        "message": message,
        "data": data
    }

    if meta is not None:
        response["meta"] = meta

    return response


def error_response(
    message: str = "Something went wrong",
    status_code: int = 400,
    errors: Any = None
):

    response = {
        "success": False,
        "message": message,
        "status_code": status_code
    }

    if errors is not None:
        response["errors"] = errors

    return response
