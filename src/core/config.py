from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    
    
    PROJECT_NAME: str = "E-commerce Generator"
    DEBUG: bool = True
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",           # Откуда брать переменные
        env_file_encoding="utf-8", # Кодировка файла
        case_sensitive=False,      # Игнорировать регистр (LOG_LEVEL = log_level)
        extra="forbid"             # Запретить неизвестные поля (защита от опечаток)
    )
    
    
    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    
settings = Settings()