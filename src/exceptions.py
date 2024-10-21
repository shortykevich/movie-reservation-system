from starlette import status
from fastapi import HTTPException


WrongCredentialException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Wrong credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
UserInactiveException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
)
UnauthorizedException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authorization failed",
    headers={"WWW-Authenticate": "Bearer"},
)
