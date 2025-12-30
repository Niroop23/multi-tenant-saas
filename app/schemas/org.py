from pydantic import BaseModel
from uuid import UUID
from datetime import datetime



class OrgCreate(BaseModel):
    name:str
    
    

class OrgResponse(BaseModel):
    id:UUID
    name:str
    role:str
    created_at:datetime
    
    
    model_config={
        "from_attributes":True
    }