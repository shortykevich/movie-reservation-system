from passlib.context import CryptContext

from src.auth.schemas import UserRequest


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_pwd_hash(password):
    return pwd_context.hash(password)


def verify_pwd(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user_with_hashed_pwd(user: UserRequest) -> dict:
    dumped_user = user.model_dump()
    dumped_user['password'] = get_pwd_hash(dumped_user['password'])
    return dumped_user
