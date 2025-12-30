from uuid import UUID
from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import required_org_role
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.schemas.org import OrgCreate, OrgResponse


router=APIRouter(prefix="/orgs",tags=["Organizations"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=OrgResponse,
    responses={
        409: {
            "description": "Conflict",
            "content": {"application/json": {"example": {"detail": "organization already exists"}}},
        }
    },
)
def create_org(payload:OrgCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    
    existing=db.query(Organization).filter(Organization.name==payload.name).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="organization already exists")
    
    org=Organization(name=payload.name)
    db.add(org)
    db.flush()
    
    membership=Membership(
        user_id=current_user.id,
        org_id=org.id,
        role="owner"
    )
    
    db.add(membership)
    db.commit()
    db.refresh(org)
    
    
    return{
        "id":org.id,
        "name":org.name,
        "role":"owner",
        "created_at":org.created_at
    }
    
    
@router.get("",response_model=list[OrgResponse])
def list_orgs(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    memberships=(
        db.query(Membership,Organization)
        .join(Organization,Membership.org_id==Organization.id).filter(
            Membership.user_id==current_user.id
        )
        .all()
    )
    
    return [
        {
            "id":org.id,
            "name":org.name,
            "role":membership.role,
            "created_at":org.created_at,
        }
        for membership,org in memberships
    ]
    

@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(required_org_role("owner"))],
    responses={
        404: {"description": "Not Found", "content": {"application/json": {"example": {"detail": "Organization not found"}}}}
    },
)
def delete_org(org_id:UUID,db:Session=Depends(get_db)):
    
    org=db.query(Organization).filter(Organization.id == org_id).first()
    
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Organization not found")
    
    db.delete(org)
    db.commit()