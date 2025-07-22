from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    HOST: str
    PORT: int
    CLIENT_SECRETS_FILE: str = "client_secret.json"
    SCOPES: list[str] = ['https://www.googleapis.com/auth/drive.readonly']
    
    @property
    def REDIRECT_URI(self) -> str:
        return f"http://{self.HOST}:{self.PORT}/callback"

    class Config:
        env_file = ".env"

settings = Settings()
