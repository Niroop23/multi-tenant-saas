from pydantic import BaseModel
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    
    APP_NAME: str
    ENV:str = 'dev'
    
    DATABASE_URL:str
    TEST_DATABASE_URL:str
    JWT_SECRET_KEY:str="01B028C63E81CEE19AB544CF9A976E75F070D285B0684B05C93E97A495AB568D"
    JWT_ALGORITHM:str= "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int =30
    REFRESH_TOKEN_EXPIRE_DAYS:int=7
    INVITE_EXPIRE_DAYS:int =7
    
    
    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )
    
    
settings=Settings()