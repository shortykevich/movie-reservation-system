from passlib.context import CryptContext

from src.users.schemas import UserCreateRequest


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_pwd_hash(password):
    return pwd_context.hash(password)


def verify_pwd(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_user_pwd(user: UserCreateRequest) -> dict:
    """Return user's data with hashed password"""
    user_data = user.model_dump()
    user_data["password"] = get_pwd_hash(user_data["password"])
    return user_data
