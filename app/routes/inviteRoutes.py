from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime,timezone,timedelta
from app.core.config import settings
from app.schemas.invite import InviteCreate,InviteOut
from app.core.permissions import required_org_role
from app.database.session import get_db
from app.models.org_invite import OrgInvite
from app.models.user import User
from app.core.security import get_current_user
from app.models.membership import Membership

router=APIRouter(prefix="/orgs/{org_id}/invites",tags=["Org Invites"])


@router.post(
    "",
    response_model=InviteOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "description": "Conflict",
            "content": {
                "application/json": {"example": {"detail": "Outgoing invite to this email already exists"}}
            },
        }
    },
)
def create_invite(org_id:UUID,payload:InviteCreate,db:Session=Depends(get_db),membership=Depends(required_org_role("owner","admin"))):
    
    existing=(
        db.query(OrgInvite).filter(
        OrgInvite.org_id == org_id,
        OrgInvite.email == payload.email,
        OrgInvite.status == "pending").first()
        )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,detail="Outgoing invite to this email already exists"
        )
    invite=OrgInvite(org_id=org_id,
                     email=payload.email,
                     role=payload.role,
                     invited_by=getattr(membership,"user_id",None) or membership.id,
                     expires_at=datetime.now(timezone.utc)+timedelta(days=settings.INVITE_EXPIRE_DAYS))
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    
    return invite


@router.get(
    "",
    response_model=list[InviteOut],
    dependencies=[Depends(required_org_role("owner","admin"))],
    responses={
        401: {"description": "Unauthorized", "content": {"application/json": {"example": {"detail": "Unauthorized"}}}},
        403: {"description": "Forbidden", "content": {"application/json": {"example": {"detail": "Forbidden"}}}},
    },
)
def list_invites(org_id:UUID,db:Session=Depends(get_db),_=Depends(required_org_role("admin","owner"))):
    
    return (
        db.query(OrgInvite).filter(OrgInvite.org_id==org_id).order_by(OrgInvite.created_at.desc()).all()
    )
    
@router.post(
    "/{invite_id}/accept",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Not Found", "content": {"application/json": {"example": {"detail": "Invite not found"}}}},
        400: {"description": "Bad Request", "content": {"application/json": {"example": {"detail": "Invite isnt pending"}}}},
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "examples": {
                        "expired": {"summary": "Invite expired", "value": {"detail": "Invite expired"}},
                        "email_mismatch": {"summary": "Email mismatch", "value": {"detail": "Invite email doesnt match with the current user"}},
                    }
                }
            }
        },
        409: {"description": "Conflict", "content": {"application/json": {"example": {"detail": "Already an existing member"}}}},
        200: {"description": "OK", "content": {"application/json": {"example": {"message": "Invite accepted"}}}},
    },
)
def accept_invite(org_id:UUID,
                  invite_id:UUID,
                  db:Session=Depends(get_db),
                  current_user:User=Depends(get_current_user)):
    invite=(
        db.query(OrgInvite).filter(OrgInvite.id == invite_id,OrgInvite.org_id==org_id).first()
    )
    
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invite not found")
    
    if invite.status !="pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invite isnt pending")
    
    if invite.expires_at and invite.expires_at <datetime.now(timezone.utc):
        invite.status="expired"
        db.commit()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invite expired")
    
    if invite.email.lower() != current_user.email.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invite email doesnt match with the current user")
    
    existing=(
        db.query(Membership).filter(Membership.user_id==current_user.id,Membership.org_id==org_id).first()
    )
    
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Already an existing member")
    
    membership=Membership(
        user_id=current_user.id,
        org_id=org_id,
        role=invite.role
    )
    invite.status="accepted"
    db.add(membership)
    db.commit()
    
    
    return {"message":"Invite accepted"}

@router.post(
    "/{invite_id}/revoke",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(required_org_role("owner"))],
    responses={
        404: {"description": "Not Found", "content": {"application/json": {"example": {"detail": "Invite not found"}}}},
        400: {"description": "Bad Request", "content": {"application/json": {"example": {"detail": "Invite pending"}}}},
        200: {"description": "OK", "content": {"application/json": {"example": {"message": "Invite revoked"}}}},
    },
)
def revoke_invite(org_id:UUID,invite_id:UUID,db:Session=Depends(get_db)):
    invite=(
        db.query(OrgInvite).filter(
            OrgInvite.id==invite_id,
            OrgInvite.org_id == org_id).first()
    )
    
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invite not found")
    
    if invite.status !="pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invite {invite.status}")
    
    invite.status="revoked"
    db.commit()
    
    return {"message":"Invite revoked"}