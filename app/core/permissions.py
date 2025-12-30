from fastapi import HTTPException,Depends,status

from app.core.dependencies import get_current_membership

def required_org_role(*allowed_roles:str):
    def role_checker(membership=Depends(get_current_membership)):
        if membership.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Indufficient permission")
        
        return membership
    
    return role_checker
    