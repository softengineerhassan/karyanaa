
from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> Dict[str, Any]:
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def error_response(
    message: str = "Error",
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    response = {
        "success": False,
        "message": message
    }
    
    if details:
        response["details"] = details
    
    return response


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
    stats: Optional[Any] = None
) -> Dict[str, Any]:
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    response = {
        "success": True,
        "message": message,
        "data": items,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    if stats is not None:
        response["stats"] = stats
        
    return response
