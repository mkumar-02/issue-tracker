
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User
from app.schemas.issues import IssueCreate, IssueUpdate, IssueResponse, IssueAssign
from app.core.security import get_current_user
from app.services.issue_service import (
    create_issue,
    get_project_issues,
    get_issue,
    assign_issue,
    update_issue,
    update_issue_status,
    reopen_issue
)

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post("/{project_id}", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue_endpoint(project_id: int, issue_data: IssueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_issue(db, project_id, issue_data, current_user)


@router.get("/project/{project_id}", response_model=list[IssueResponse])
def get_project_issues_endpoint(project_id: int, status_filter: str | None = None, priority: str | None = None, assignee_id: int | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_project_issues(db, project_id, current_user, status_filter, priority, assignee_id)


@router.get("/{issue_id}")
def get_issue_endpoint(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_issue(db, issue_id, current_user)


@router.patch("/{issue_id}/assign")
def assign_issue_endpoint(issue_id: int, data: IssueAssign, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return assign_issue(db, issue_id, data, current_user)


@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue_endpoint(issue_id: int, data: IssueUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_issue(db, issue_id, data, current_user)


@router.patch("/{issue_id}/status")
def update_issue_status_endpoint(issue_id: int, new_status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_issue_status(db, issue_id, new_status, current_user)


@router.patch("/{issue_id}/reopen")
def reopen_issue_endpoint(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return reopen_issue(db, issue_id, current_user)
