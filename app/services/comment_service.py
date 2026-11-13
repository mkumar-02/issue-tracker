
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Comment, Issue, ProjectMember, User
from app.schemas.comments import CommentCreate


def add_comment(db: Session, issue_id: int, data: CommentCreate, current_user: User):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.status == "closed":
        raise HTTPException(status_code=400, detail="Cannot comment on a closed issue")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    if not data.content.strip():
        raise HTTPException(status_code=422, detail="Comment cannot be blank")

    comment = Comment(
        content=data.content.strip(),
        issue_id=issue_id,
        user_id=current_user.id
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_issue_comments(db: Session, issue_id: int, current_user: User):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    return db.query(Comment).filter(
        Comment.issue_id == issue_id
    ).order_by(Comment.created_at.asc(), Comment.id.asc()).all()


def update_comment(db: Session, comment_id: int, data: CommentCreate, current_user: User):
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


def delete_comment(db: Session, comment_id: int, current_user: User):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}
