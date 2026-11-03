from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Comment, Issue, ProjectMember, User
from app.schemas.comments import CommentCreate, CommentResponse
from app.security import get_current_user

router = APIRouter(tags=["Comments"])

@router.post("/issues/{issue_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(issue_id: int, data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.status == "closed":
        raise HTTPException(status_code=400, detail="Cannot comment on a closed issue")

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()
    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    if not data.content.strip():
        raise HTTPException(status_code=422, detail="Comment cannot be blank")

    comment = Comment(content=data.content.strip(), issue_id=issue_id, user_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/issues/{issue_id}/comments", response_model=list[CommentResponse])
def get_issue_comments(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()
    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    comments = db.query(Comment).filter(Comment.issue_id == issue_id).order_by(Comment.created_at.asc(), Comment.id.asc()).all()
    return comments

@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(comment_id: int, data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own comments")

    if not data.content.strip():
        raise HTTPException(status_code=422, detail="Comment cannot be blank")

    comment.content = data.content.strip()
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}