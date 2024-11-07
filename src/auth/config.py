from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent.parent


class JWTSettings(BaseSettings):
    _access_token_expire_minutes = 60
    _refresh_token_expire_minutes = 30 * 24 * 60
    _public_key: Path = BASE_DIR / "jwt-public.pem"
    _private_key: Path = BASE_DIR / "jwt-private.pem"
    _algorithm: str = "RS256"

    def get_public_key(self) -> str:
        return self._public_key.read_text()

    def get_private_key(self) -> str:
        return self._private_key.read_text()

    def get_algorithm(self) -> str:
        return self._algorithm

    def get_access_token_expires_in_minutes(self) -> int:
        return self._access_token_expire_minutes

    def get_refresh_token_expires_in_minutes(self) -> int:
        return self._refresh_token_expire_minutes


jwt_settings = JWTSettings()
