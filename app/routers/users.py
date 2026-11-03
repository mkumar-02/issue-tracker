from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.security import  get_current_admin
from app.database import get_db
from app.models import User
from app.schemas.users import UserResponse
from app.security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return db.query(User).all()