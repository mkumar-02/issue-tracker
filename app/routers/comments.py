
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User
from app.schemas.comments import CommentCreate, CommentResponse
from app.core.security import get_current_user
from app.services.comment_service import (
    add_comment,
    get_issue_comments,
    update_comment,
    delete_comment
)

router = APIRouter(tags=["Comments"])


@router.post("/issues/{issue_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment_endpoint(issue_id: int, data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return add_comment(db, issue_id, data, current_user)


@router.get("/issues/{issue_id}/comments", response_model=list[CommentResponse])
def get_issue_comments_endpoint(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_issue_comments(db, issue_id, current_user)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def update_comment_endpoint(comment_id: int, data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_comment(db, comment_id, data, current_user)


@router.delete("/comments/{comment_id}")
def delete_comment_endpoint(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_comment(db, comment_id, current_user)
    return {"message": "Comment deleted successfully"}
