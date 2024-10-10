from src.constants import ROLES_MAPPING
from src.users.models import RoleName


def get_role_id_by_name(role_name: RoleName) -> int | None:
    return ROLES_MAPPING.get(role_name, None)


def get_role_name_by_id(role_id: int) -> RoleName | None:
    return next(
        filter(lambda role: role[1] == role_id, ROLES_MAPPING.values()),
        None
    )
