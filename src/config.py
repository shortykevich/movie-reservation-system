from pydantic import SecretStr
from pydantic_settings import BaseSettings


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


settings = Settings(_env_file='.env')
