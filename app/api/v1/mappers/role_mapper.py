from app.api.v1.schemas.role_schemas import RoleResponse, RoleDetailResponse
from app.models.role import Role


def map_role_to_role_response(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        created_at=role.created_at,
        updated_at=role.updated_at,
    )


def map_role_to_role_detail_response(role: Role) -> RoleDetailResponse:
    return RoleDetailResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=[
            {
                "id": rp.permission.id,
                "name": rp.permission.name,
                "code": rp.permission.code,
            }
            for rp in getattr(role, "role_permissions", [])
            if rp.permission is not None
        ],
    )
