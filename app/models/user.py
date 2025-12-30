from sqlalchemy import Column,String,DateTime,Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database.base import Base


class User(Base):
    __tablename__="users"
    
    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    email=Column(String(255),unique=True,index=True,nullable=False)
    username=Column(String(32),unique=True,index=True,nullable=False)
    password_hash=Column(String(255),nullable=False)
    is_active=Column(Boolean,nullable=False,server_default=text("true"))
    created_at=Column(DateTime(timezone=True),server_default=func.now())