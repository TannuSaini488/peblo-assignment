from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    postgres_user: str = "peblo"
    postgres_password: str = "peblo_dev"
    postgres_db: str = "peblo_tv"
    database_url: str = Field(..., env='DATABASE_URL')
    
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 480
    
    storage_backend: str = "local"
    storage_local_path: str = "/app/storage"
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"
    default_editor_username: str = "editor"
    default_editor_password: str = "editor123"

    @property
    def get_cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"

settings = Settings()
