from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str ="bearer"
    
class TokenData(BaseModel):
    id:UUID
    org_id:Optional[UUID] =None
    role:Optional[str] =None