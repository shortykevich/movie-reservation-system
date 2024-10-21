from typing import Optional

from src.constants import ROLES_MAPPING
from src.users.models import RoleName


def get_role_id_by_name(role_name: RoleName) -> Optional[int]:
    return ROLES_MAPPING.get(role_name, None)


def get_role_name_by_id(role_id: int) -> Optional[RoleName]:
    role = next((item for item in ROLES_MAPPING.items() if item[1] == role_id), None)
    return role[0] if role else None
