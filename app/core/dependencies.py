from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header, status
from app.core.security import get_current_user, verify_access_token
from app.database.session import get_db
from app.models.membership import Membership
from app.models.user import User
from app.schemas.token import TokenData
from app.core.security import bearer_scheme

def get_current_membership(
    org_id: UUID | None = None,
    org_header_id: UUID | None = Header(None, alias="X-Org-Id"),
    db: Session = Depends(get_db),
    credentials= Depends(bearer_scheme)
):
    # If both are provided, they MUST match
    if org_id and org_header_id and org_id != org_header_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Org ID mismatch between path and X-Org-Id header",
        )
        
    creds_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="couldn't validate credentials")
    
    token_data=verify_access_token(credentials.credentials,creds_exception)

    effective_org_id = org_id or org_header_id

    if not effective_org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization id is missing ",
        )
    if token_data.org_id== effective_org_id and token_data.role:
        return token_data

    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == token_data.id,
            Membership.org_id == effective_org_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )

    return membership
