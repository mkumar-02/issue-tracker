
from sqlalchemy.orm import Session
from app.models import User


def get_all_users(db: Session):
    return db.query(User).all()
