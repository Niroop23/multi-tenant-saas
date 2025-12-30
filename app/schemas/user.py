from datetime import datetime
import re
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    username:str =Field(...,pattern=r"^[a-z0-9_]+$")
    password:str
    
    @field_validator("username")
    @classmethod
    def username_check(cls,v:str):
        v=v.lower()
        
        if len(v)>32:
            raise ValueError("Username must be less than 32 characters")
        
        if not re.fullmatch(r"[a-z0-9_]+$",v):
            raise ValueError("Username can only contain lowercase letters, numbers and underscore")
        return v
    
class UserOut(BaseModel):
    id:UUID
    email:EmailStr
    username:str
    created_at:datetime
    
    
    model_config={
        "from_attributes":True
    }