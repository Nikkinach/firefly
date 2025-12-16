"""
User management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.user import UserUpdate, UserResponse, UserPreferencesUpdate, UserPreferencesResponse
from app.services.user import UserService
from app.services.audit import AuditService
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    request: Request,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    updated_user = UserService.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    AuditService.log_action(
        db=db,
        action_type="USER_PROFILE_UPDATED",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )

    return updated_user


@router.get("/me/preferences", response_model=UserPreferencesResponse)
def get_my_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user preferences"""
    if not current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    return current_user.preferences


@router.put("/me/preferences", response_model=UserPreferencesResponse)
def update_my_preferences(
    request: Request,
    prefs_data: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user preferences"""
    updated_prefs = UserService.update_preferences(db, current_user.id, prefs_data)
    if not updated_prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )

    AuditService.log_action(
        db=db,
        action_type="USER_PREFERENCES_UPDATED",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )

    return updated_prefs


@router.get("/me/export")
def export_my_data(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export all user data (GDPR/CCPA compliance)"""
    data = UserService.export_user_data(db, current_user.id)

    AuditService.log_sensitive_data_export(
        db=db,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else "unknown",
        export_type="full_data_export"
    )

    return data


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user account and all data (Right to be Forgotten)"""
    user_id = current_user.id

    # Log before deletion
    AuditService.log_action(
        db=db,
        action_type="USER_ACCOUNT_DELETED",
        user_id=user_id,
        ip_address=request.client.host if request.client else None
    )

    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )

    return None
