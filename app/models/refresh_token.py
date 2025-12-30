from sqlalchemy import Column,DateTime,ForeignKey,Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..database.base import Base


class RefreshToken(Base):
    __tablename__="refresh_tokens"
    
    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id=Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    token_hash=Column(UUID(as_uuid=True),nullable=False,unique=True)
    is_revoked=Column(Boolean,default=False,nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())