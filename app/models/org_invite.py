from sqlalchemy import Column, ForeignKey,String,DateTime,Enum,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database.base import Base


class OrgInvite(Base):
    __tablename__ = "org_invites"
    __table_args__=(UniqueConstraint("org_id","email",name="uq_org_invite_email"),)
    
    id= Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    
    org_id=Column(UUID(as_uuid=True),ForeignKey("organizations.id",ondelete="CASCADE"),nullable=False,)
    email=Column(String,nullable=False,index=True)
    role=Column(String,nullable=False)
    invited_by =Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="SET NULL"),)
    
    status=Column(Enum("pending","accepted","revoked","expired",name="invite_status"),nullable=False,default="pending")
    expires_at=Column(DateTime(timezone=True),nullable=True)
    created_at=Column(DateTime(timezone=True),server_default=func.now())