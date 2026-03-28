# StandardResponse Format - API-Wide Implementation ✅

## Overview

All API endpoints across the entire application have been standardized to use the `StandardResponse[T]` wrapper format. This ensures consistent response structure, better error handling, and improved API consistency.

---

## Response Format

**Structure:**
```json
{
  "success": true,
  "message": "Human-readable message describing the operation",
  "data": { /* T - The actual response data */ },
  "errors": null  /* Only present if there are validation errors */
}
```

**Fields:**
- `success` (boolean): Whether the operation was successful
- `message` (string): Human-readable message
- `data` (T): The actual response payload (can be object, array, or null)
- `errors` (optional list): Error details if present

---

## Implementation Details

### Route Configuration

All routes use the pattern:
```python
@router.get("/endpoint", response_model=StandardResponse[ResponseType])(handler)
@router.post("/endpoint", response_model=StandardResponse[ResponseType])(handler)
```

### Response Creation

Routes delegate to handlers → handlers delegate to actions → actions use `success_response()`:

```python
# In actions file
from app.core.response import success_response

def create_item(...):
    # ... business logic ...
    return success_response(data=item_data, message="Item created successfully")
```

### Standard Helper Function

Located in `app/core/response.py`:
```python
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
```

---

## API Modules Using StandardResponse

### 1. **Authentication** - `app/api/v1/routes/auth.py`
All endpoints wrapped with `StandardResponse`:
- `POST /auth/login` → `StandardResponse[LoginResponse]`
- `POST /auth/register` → `StandardResponse[RegisterResponse]`
- `POST /auth/refresh` → `StandardResponse[RefreshTokenResponse]`
- `GET /auth/me` → `StandardResponse[CurrentUserResponse]`
- `POST /auth/verify-otp` → `StandardResponse[None]`
- `POST /auth/logout` → `StandardResponse[None]`

### 2. **User Management** - `app/api/v1/routes/users.py`
All endpoints wrapped with `StandardResponse`:
- `GET /users` → `StandardResponse[UserListResponse]`
- `POST /users` → `StandardResponse[UserResponse]`
- `GET /users/{id}` → `StandardResponse[UserDetailResponse]`
- `PUT /users/{id}` → `StandardResponse[UserResponse]`
- `DELETE /users/{id}` → `StandardResponse[None]`
- `PUT /users/me/profile` → `StandardResponse[CurrentUserResponse]`
- `POST /users/me/profile-picture` → `StandardResponse[CurrentUserResponse]`

### 3. **Inventory** - `app/api/v1/routes/inventory.py`
All endpoints wrapped with `StandardResponse`:
- **Categories**: CRUD operations → `StandardResponse[CategoryResponse]`
- **Products**: CRUD operations → `StandardResponse[ProductResponse]`
- **Suppliers**: CRUD operations → `StandardResponse[SupplierResponse]`
- **Units**: CRUD operations → `StandardResponse[UnitResponse]`
- **Purchases**: Create/List → `StandardResponse[PurchaseResponse]`
- **Stock Movements**: List → `StandardResponse[List[StockMovementResponse]]`
- **Riders**: CRUD operations → `StandardResponse[RiderResponse]`

### 4. **Riders** - `app/api/v1/routes/riders.py`
All endpoints wrapped with `StandardResponse`:
- `GET /riders` → `StandardResponse[List[RiderProfileResponse]]`
- `POST /riders` → `StandardResponse[RiderProfileResponse]`
- `GET /riders/{id}` → `StandardResponse[RiderProfileResponse]`
- `PUT /riders/{id}` → `StandardResponse[RiderProfileResponse]`
- `DELETE /riders/{id}` → `StandardResponse[None]`

### 5. **Items** - `app/api/v1/routes/items.py`
All endpoints wrapped with `StandardResponse`:
- `GET /items` → `StandardResponse[List[RiderItemResponse]]`
- `POST /items` → `StandardResponse[RiderItemResponse]`
- `GET /items/{id}` → `StandardResponse[RiderItemResponse]`
- `PUT /items/{id}` → `StandardResponse[RiderItemResponse]`
- `DELETE /items/{id}` → `StandardResponse[None]`

### 6. **Sales** - `app/api/v1/routes/sales.py`
All endpoints wrapped with `StandardResponse`:
- **Customers**: CRUD operations → `StandardResponse[CustomerResponse]`
- **Sales**: Create/List/Get → `StandardResponse[SaleResponse]`
- **Payments**: Add payment → `StandardResponse[SaleResponse]`
- **Cancellation**: Cancel sale → `StandardResponse[SaleResponse]`

---

## Recent Changes

### Modified Files

1. **app/api/v1/routes/sales.py**
   - Changed all response_model declarations from direct types to `StandardResponse[T]`
   - Added import: `from app.core.response import success_response`
   - Updated all handlers to wrap responses with `success_response()`
   - All 11 endpoints now use StandardResponse

2. **app/api/v1/routes/users.py**
   - Fixed: Changed `GET /users` response from `UserListResponse` to `StandardResponse[UserListResponse]`

### Verified Files (Already Compliant)

- ✅ `app/api/v1/routes/auth.py` - All endpoints use `StandardResponse[T]`
- ✅ `app/api/v1/routes/inventory.py` - All endpoints use `StandardResponse[T]`
- ✅ `app/api/v1/routes/riders.py` - All endpoints use `StandardResponse[T]`
- ✅ `app/api/v1/routes/items.py` - All endpoints use `StandardResponse[T]`

---

## Example Responses

### Success with Data (List)
```json
{
  "success": true,
  "message": "Customers retrieved successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "phone": "+923001234567",
      "customer_type": "regular",
      "current_balance": 5000.00,
      "created_at": "2026-03-28T10:30:50.421068+05:00"
    }
  ],
  "errors": null
}
```

### Success with Data (Object)
```json
{
  "success": true,
  "message": "Sale created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "sale_number": "SAL-20260328-00001",
    "grand_total": 5887.50,
    "payment_status": "paid",
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "quantity": 20.0,
        "unit_price": 150.00,
        "line_total": 2800.00
      }
    ],
    "created_at": "2026-03-28T10:30:50.421068+05:00"
  },
  "errors": null
}
```

### Success without Data
```json
{
  "success": true,
  "message": "Category deleted successfully",
  "data": null,
  "errors": null
}
```

---

## Testing

### Test Files Created
- `tmp/test_standard_response.py` - Tests sales endpoints
- `tmp/test_all_endpoints.py` - Tests all endpoint response formats
- `tmp/verify_standard_response.py` - Verification script

### Verification Results
```
✅ Sales - List Customers (GET) - Returns StandardResponse[List[CustomerResponse]]
✅ Sales - List Sales (GET) - Returns StandardResponse[List[SaleListResponse]]
✅ Sales - Get Sale (GET) - Returns StandardResponse[SaleResponse]
✅ Sales - Create Sale (POST) - Returns StandardResponse[SaleResponse]
✅ Sales - Create Customer (POST) - Returns StandardResponse[CustomerResponse]
```

---

## Benefits

1. **Consistency**: All APIs follow the same response structure
2. **Predictability**: Frontend can rely on `success`, `message`, and `data` fields
3. **Error Handling**: Unified error response format with `errors` array
4. **Type Safety**: Pydantic validation ensures response data matches type `T`
5. **Documentation**: Clear, self-documenting response format
6. **Client Experience**: Consistent handling of success/failure cases

---

## Migration Guide for Developers

When adding new endpoints, follow this pattern:

```python
# 1. Import StandardResponse and success_response
from app.api.v1.schemas.common_schema import StandardResponse
from app.core.response import success_response

# 2. Define route with StandardResponse[T]
@router.post("/items", response_model=StandardResponse[ItemResponse], status_code=status.HTTP_201_CREATED)
def create_item(req: ItemCreateRequest, handler: ItemHandler = Depends(get_item_handler)):
    """Create a new item."""
    item = handler.handle_create_item(req)
    return success_response(data=item, message="Item created successfully")

# 3. In handlers/actions, use success_response()
return success_response(
    data=item_response,
    message="Item operation successful"
)
```

---

## Standard HTTP Status Codes with StandardResponse

- `200` - GET, PUT successful
- `201` - POST successful (create)
- `204` - DELETE successful
- `400` - Bad request (validation error)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `422` - Validation error (unprocessable entity)
- `500` - Server error

---

**Implementation Date**: 2026-03-28  
**Status**: ✅ COMPLETE - All APIs use StandardResponse format
