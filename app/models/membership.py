from sqlalchemy import Column, ForeignKey,String,DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.base import Base


class Membership(Base):
    __tablename__ ="memberships"
    
    user_id=Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    org_id=Column(UUID(as_uuid=True),ForeignKey("organizations.id",ondelete="CASCADE"),primary_key=True)
    role=Column(String,nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())