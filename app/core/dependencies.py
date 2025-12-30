from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header, status
from app.core.security import get_current_user, verify_access_token
from app.database.session import get_db
from app.models.membership import Membership
from app.models.user import User
from app.schemas.token import TokenData


def get_current_membership(
    org_id: UUID | None = None,
    org_header_id: UUID | None = Header(None, alias="X-Org-Id"),
    current_user: User = Depends(get_current_user),
    token_data:TokenData=Depends(verify_access_token),
    db: Session = Depends(get_db),
):
    # If both are provided, they MUST match
    if org_id and org_header_id and org_id != org_header_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Org ID mismatch between path and X-Org-Id header",
        )
    
    if token_data.org_id:
        return Membership(
            user_id=current_user.id,
            org_id=token_data.org_id,
            role=token_data.role,
        )

    effective_org_id = org_id or org_header_id

    if not effective_org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization id is missing (path param or X-Org-Id header)",
        )

    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == current_user.id,
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
