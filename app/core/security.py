from uuid import UUID, uuid4
from fastapi import Depends, HTTPException,status
from fastapi.security import  HTTPAuthorizationCredentials,HTTPBearer
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.schemas.token import TokenData
from app.database.session import get_db
from app.core.config import settings
from app.models.user import User

pwd_context=CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)
bearer_scheme=HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain:str, hashed:str)->bool:
    return pwd_context.verify(plain,hashed)


#jwt_stuff

def create_access_token(user_id: UUID, org_id: UUID | None = None, role: str | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }
    
    if org_id:
        payload["org_id"]=str(org_id)
        
    if role:
        payload["role"]=role
    
    jwt_encoded=jwt.encode(payload,settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
    
    return jwt_encoded   


def verify_access_token(token: str, creds_exception: None = None):
    if creds_exception is None:
        creds_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload=jwt.decode(token,settings.JWT_SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
        
        user_id_str:str=payload.get("sub")
        token_type=payload.get("type")
        
        if user_id_str is None or token_type!="access":
            raise creds_exception
        
        user_id=UUID(user_id_str)
        return TokenData(id=user_id,
                         org_id=UUID(payload["org_id"]) if payload.get("org_id") else None,
                         role=payload.get("role"),
                         )
    
    except (JWTError, ValueError,KeyError):
        raise creds_exception
    
def create_refresh_token(user_id:UUID)->tuple[str,UUID]:
    
    jti=uuid4()
    
    expire = datetime.now(timezone.utc)+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload={
        "sub":str(user_id),
        "type":"refresh",
        "jti":str(jti),
        "exp":expire,
    }
    
    token=jwt.encode(payload,settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
    return token,jti

def decode_and_verify_refresh_token(token:str)->tuple[UUID,UUID]:
    
    try:
        payload=jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type")!="refresh":
            raise ValueError()
        
        return UUID(payload["sub"]),UUID(payload.get("jti"))
    
    except(JWTError,ValueError,TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme),db:Session=Depends(get_db)):
    creds_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Couldn't validate credentials",headers={"WWW-Authenticate":"Bearer"})
    
    token=credentials.credentials
    
    token_data=verify_access_token(token,creds_exception)
    
    user=db.query(User).filter(User.id==token_data.id).first()
    
    if user is None:
        raise creds_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    user._token_org_id =token_data.org_id
    user._token_role = token_data.role
    
    return user