from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent.parent


class TokenSettings(BaseSettings):
    _ACCESS_TOKEN_EXPIRE_MINUTES = 60
    public_key: Path = BASE_DIR / 'jwt-public.pem'
    private_key: Path = BASE_DIR / 'jwt-private.pem'
    algorithm: str = "RS256"

    def get_public_key(self) -> str:
        return self.public_key.read_text()

    def get_private_key(self) -> str:
        return self.private_key.read_text()

    def get_algorithm(self) -> str:
        return self.algorithm

    def get_access_token_expires_in(self) -> int:
        """Token expires in *minutes*"""
        return self._ACCESS_TOKEN_EXPIRE_MINUTES


token_settings = TokenSettings()
