from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Issue, Project, ProjectMember, User
from app.schemas.issues import IssueCreate, IssueUpdate, IssueResponse,IssueAssign
from app.security import get_current_user

router = APIRouter(prefix="/issues", tags=["Issues"])

@router.post("/{project_id}", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(project_id: int, issue_data: IssueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    if issue_data.priority not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Invalid priority")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    last_issue = db.query(Issue).filter(Issue.project_id == project_id).order_by(Issue.issue_number.desc()).first()
    issue_number = last_issue.issue_number + 1 if last_issue else 1

    issue = Issue(title=issue_data.title.strip(), description=issue_data.description, priority=issue_data.priority, labels=issue_data.labels, project_id=project_id, created_by_id=current_user.id, issue_number=issue_number)
    if not issue.title:
        raise HTTPException(status_code=422, detail="Title cannot be blank")

    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

@router.get("/project/{project_id}", response_model=list[IssueResponse])
def get_project_issues(project_id: int, status_filter: str | None = None, priority: str | None = None, assignee_id: int | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id).first()

    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    query = db.query(Issue).filter(Issue.project_id == project_id)

    if status_filter:
        query = query.filter(Issue.status == status_filter)

    if priority:
        query = query.filter(Issue.priority == priority)

    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)

    return query.order_by(Issue.issue_number).all()

@router.get("/{issue_id}")
def get_issue(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()
    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    return {
        "id": issue.id,
        "issue_number": issue.issue_number,
        "title": issue.title,
        "description": issue.description,
        "priority": issue.priority,
        "status": issue.status,
        "labels": issue.labels,
        "project_id": issue.project_id,
        "created_by_id": issue.created_by_id,
        "assignee_id": issue.assignee_id,
        "comments": [
            {
                "id": comment.id,
                "content": comment.content,
                "user_id": comment.user_id,
                "created_at": comment.created_at
            }
            for comment in issue.comments
        ]
    }

@router.patch("/{issue_id}/assign")
def assign_issue(issue_id: int, data: IssueAssign, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.status == "closed":
        raise HTTPException(status_code=400, detail="Reopen the issue before modifying it")

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()
    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    if data.assignee_id is not None:
        assignee_membership = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == data.assignee_id).first()
        if not assignee_membership:
            raise HTTPException(status_code=400, detail="Assignee must be a member of this project")

    issue.assignee_id = data.assignee_id
    db.commit()
    db.refresh(issue)
    return {"message": "Issue assigned successfully" if data.assignee_id else "Issue unassigned successfully", "issue_id": issue.id, "assignee_id": issue.assignee_id}

@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue(issue_id: int, data: IssueUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()
    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    if issue.status == "closed":
        raise HTTPException(status_code=400, detail="Reopen the issue before updating it")

    updates = data.model_dump(exclude_unset=True)

    if "title" in updates and not updates["title"].strip():
        raise HTTPException(status_code=422, detail="Title cannot be blank")

    if "priority" in updates and updates["priority"] not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Invalid priority")

    if "status" in updates:
        raise HTTPException(status_code=400, detail="Use the status transition endpoint to change status")

    for key, value in updates.items():
        if key == "title":
            value = value.strip()
        setattr(issue, key, value)

    db.commit()
    db.refresh(issue)
    return issue

@router.patch("/{issue_id}/status")
def update_issue_status(issue_id: int, new_status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()

    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    is_project_admin = membership and membership.project_role == "admin"
    is_assignee = current_user.id == issue.assignee_id

    if current_user.role != "admin" and not is_project_admin and not is_assignee:
        raise HTTPException(status_code=403, detail="Only the assignee or project admin can change issue status")

    transitions = {"open": "in_progress", "in_progress": "in_review", "in_review": "done", "done": "closed"}

    if issue.status == "closed":
        raise HTTPException(status_code=400, detail="Reopen the issue before changing its status")

    if transitions.get(issue.status) != new_status:
        raise HTTPException(status_code=400, detail=f"Invalid transition from {issue.status} to {new_status}")

    issue.status = new_status
    db.commit()
    db.refresh(issue)
    return {"message": "Issue status updated successfully", "status": issue.status}

@router.patch("/{issue_id}/reopen")
def reopen_issue(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == issue.project_id, ProjectMember.user_id == current_user.id).first()

    if current_user.role != "admin" and not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    is_project_admin = membership and membership.project_role == "admin"
    is_assignee = current_user.id == issue.assignee_id

    if current_user.role != "admin" and not is_project_admin and not is_assignee:
        raise HTTPException(status_code=403, detail="Only the assignee or project admin can reopen an issue")

    if issue.status != "closed":
        raise HTTPException(status_code=400, detail="Only closed issues can be reopened")

    issue.status = "open"
    db.commit()
    db.refresh(issue)
    return {"message": "Issue reopened successfully", "status": issue.status}