from pydantic import BaseModel,EmailStr
from datetime import datetime
from uuid import UUID

class InviteCreate(BaseModel):
    email:EmailStr
    role:str
    
class InviteOut(BaseModel):
    id:UUID
    org_id:UUID
    email:EmailStr
    role:str
    invited_by:UUID|None
    status:str
    expires_at: datetime | None
    created_at: datetime
    
    model_config={
        "from_attributes":True
    }