from app.api.v1.schemas.permission_schemas import PermissionResponse, PermissionDetailResponse
from app.models.permission import Permission


def map_permission_to_permission_response(permission: Permission) -> PermissionResponse:
    return PermissionResponse(
        id=permission.id,
        name=permission.name,
        description=permission.description,
        resource=permission.resource,
        action=permission.action,
        created_at=permission.created_at,
        updated_at=permission.updated_at,
    )


def map_permission_to_permission_detail_response(permission: Permission) -> PermissionDetailResponse:
    return PermissionDetailResponse(
        id=permission.id,
        name=permission.name,
        code=permission.code,
        description=permission.description,
        resource=permission.resource,
        action=permission.action,
        created_at=permission.created_at,
        updated_at=permission.updated_at,
        roles=[
            {
                "id": rp.role.id,
                "name": rp.role.name,
            }
            for rp in getattr(permission, "role_permissions", [])
            if rp.role is not None
        ],
    )
