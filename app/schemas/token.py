from uuid import UUID
from pydantic import BaseModel


class Token(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str ="bearer"
    
class TokenData(BaseModel):
    id:UUID
    org_id:UUID|None =None
    role:str|None =None