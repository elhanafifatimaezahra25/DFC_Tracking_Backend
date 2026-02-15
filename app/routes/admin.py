from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlmodel import Session, select
from ..models.user import User
from ..core.security import get_current_admin
from ..services.dashboard import get_admin_dashboard
from .. import database

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard")
def admin_dashboard(session: Session = Depends(database.get_session), current_user: User = Depends(get_current_admin)):
    """
    Get comprehensive admin dashboard.
    Requires admin privileges.
    
    Returns:
    - Summary metrics (total DFC, ECO, users)
    - DFC statistics by type and project
    - Feasibility rates and average delays
    - Status distribution
    """
    try:
        dashboard = get_admin_dashboard(session)
        return dashboard
    except Exception as e:
        logging.exception("Dashboard generation failed")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

@router.get("/users")
def list_users(session: Session = Depends(database.get_session), current_user: User = Depends(get_current_admin)):
    """List all users. Requires admin privileges."""
    users = session.exec(select(User)).all()
    return users

@router.post("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, session: Session = Depends(database.get_session), current_user: User = Depends(get_current_admin)):
    """Deactivate a user. Requires admin privileges."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # placeholder: set role to 'inactive'
    user.role = 'inactive'
    session.add(user)
    session.commit()
    return {"ok": True}
