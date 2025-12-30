from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.membership import Membership
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.token import Token
from app.schemas.user import UserCreate,UserOut
from app.core.security import create_access_token, decode_and_verify_refresh_token, get_current_user, hash_password, verify_password,create_refresh_token

router=APIRouter(prefix="/auth",tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    responses={
        409: {
            "description": "Conflict",
            "content": {
                "application/json": {"example": {"detail": "User already exists"}}
            },
        }
    },
)
def register_user(payload:UserCreate,db:Session=Depends(get_db)):
    username=payload.username.lower()
    
    existing=db.query(User).filter((User.email==payload.email) | (User.username==username)).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")
    
    user = User(
        email=payload.email,
        username=username,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {"example": {"detail": "Invalid credentials"}}
            },
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {"example": {"detail": "Inactive user"}}
            },
        },
    },
)
def login(payload:LoginRequest,db:Session=Depends(get_db)):
    user=(db.query(User).filter(
        or_(
            User.email==payload.identifier,
            User.username == payload.identifier.lower(),
        )
    ).first())
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    if not verify_password(payload.password,user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",)
        
    access_token=create_access_token(user.id)
    refresh_token,jti=create_refresh_token(user.id)
    
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=jti,
        )
    )
    db.commit()
    
    return {
        "access_token":access_token,
        "refresh_token":refresh_token,
        "token_type":"bearer",
    }
    
@router.post(
    "/login/org/{org_id}",
    response_model=Token,
    responses={
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {"example": {"detail": "Invalid credentials"}}
            },
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "examples": {
                        "inactive": {"summary": "Inactive user", "value": {"detail": "Inactive user"}},
                        "not_member": {"summary": "Not a member", "value": {"detail": "Not a member of this organization"}},
                    }
                }
            },
        },
    },
)
def login_with_org(
    org_id:UUID,
    payload:LoginRequest,
    db:Session=Depends(get_db)
):
    user=(
        db.query(User).filter(
            or_(
            User.email==payload.identifier,
            User.username == payload.identifier.lower(),
            )       
        ).first()
    )
    
    if not user or not verify_password(payload.password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Inactive user")
    
    membership=(
        db.query(Membership).filter(
            Membership.user_id == user.id,
            Membership.org_id == org_id,
        ).first()
    )
    
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not a member of this organization")
    
    access_token=create_access_token(
        user_id=user.id,
        org_id=org_id,
        role=membership.role,
    )
    
    refresh_token,jti=create_refresh_token(user.id)
    
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=jti,
    ))
    
    db.commit()
    
    return {
        "access_token":access_token,
        "refresh_token":refresh_token,
        "token_type":"bearer",
    }
    
    
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Unauthorized"}}},
        }
    },
)
def logout(refresh_token:str,db:Session=Depends(get_db)):
    
    user_id,jti=decode_and_verify_refresh_token(refresh_token)
    token_entry=(
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.token_hash == jti,
            RefreshToken.is_revoked == False,
        )
        .first()
    )
    
    if not token_entry:
        return
    
    token_entry.is_revoked=True
    db.commit()
    
@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Unauthorized"}}},
        }
    },
)
def logout_all(current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked == False,
    ).update({"is_revoked":True})
    
    db.commit()
    
    
    
@router.post(
    "/refresh",
    response_model=Token,
    responses={
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {"example": {"detail": "Refresh token revoked or reused"}}
            },
        }
    },
)
def refresh_token(refresh_token:str,db:Session=Depends(get_db)):
    user_id,jti=decode_and_verify_refresh_token(refresh_token)
    
    token_entry=(
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.token_hash == jti,
            RefreshToken.is_revoked == False,
        )
        .first()
    )
    
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token revoked or reused",
        )
        
    token_entry.is_revoked=True
    
    access_token=create_access_token(user_id=user_id)
    new_refresh_token,new_jti=create_refresh_token(user_id)
    
    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=new_jti,
        )
    )
    
    db.commit()
    
    return {
        "access_token":access_token,
        "refresh_token":new_refresh_token,
        "token_type":"bearer",
    }