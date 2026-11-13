
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User
from app.schemas.users import UserResponse
from app.core.security import get_current_user, get_current_admin
from app.services.user_service import get_all_users

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserResponse])
def get_all_users_endpoint(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return get_all_users(db)
