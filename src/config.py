from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    secret_key: SecretStr

    db_driver: str
    db_user: str
    db_pwd: SecretStr
    db_host: str
    db_port: int
    db_name: str

    def get_database_url(self) -> str:
        return (f'{self.db_driver}://{self.db_user}:{self.db_pwd.get_secret_value()}@'
                f'{self.db_host}:{self.db_port}/{self.db_name}')

    def get_secret_key(self) -> str:
        return self.secret_key.get_secret_value()


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


settings = Settings(_env_file='.env')
token_settings = TokenSettings()
