
from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


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
        response["data"] = jsonable_encoder(data)
    
    return jsonable_encoder(response)


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
        response["details"] = jsonable_encoder(details)
    
    return jsonable_encoder(response)


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
        response["stats"] = jsonable_encoder(stats)
    response["data"] = jsonable_encoder(items)
        
    return jsonable_encoder(response)
