from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    CREDENTIALS : str
    model_config = SettingsConfigDict(env_file=".env")