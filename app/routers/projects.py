from sqlalchemy.orm import Session
from app.schemas.projects import ProjectMemberAdd
from app.database import get_db
from app.models import Project, ProjectMember, User
from app.schemas.projects import ProjectCreate, ProjectResponse
from app.security import get_current_admin, get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Project, ProjectMember, User, Issue
router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

def check_project_admin(project_id: int, db: Session, current_user: User):
    if current_user.role == "admin":
        return

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id).first()

    if not membership or membership.project_role != "admin":
        raise HTTPException(status_code=403, detail="Project admin access required")


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    new_project = Project(name=project_data.name, description=project_data.description, created_by_id=current_admin.id)

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    membership = ProjectMember(project_id=new_project.id, user_id=current_admin.id, project_role="admin")
    db.add(membership)
    db.commit()

    return new_project

@router.get(
    "/",
    response_model=list[ProjectResponse]
)
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = (
        db.query(Project)
        .join(ProjectMember)
        .filter(ProjectMember.user_id == current_user.id)
        .all()
    )

    return projects

@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
def add_project_member(project_id: int, member_data: ProjectMemberAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    check_project_admin(project_id, db, current_user)

    user = db.query(User).filter(User.id == member_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="User is already a project member")

    membership = ProjectMember(project_id=project_id, user_id=user.id, project_role="member")
    db.add(membership)
    db.commit()
    return {"message": "Project member added successfully"}


@router.delete("/{project_id}/members/{user_id}")
def remove_project_member(project_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    check_project_admin(project_id, db, current_user)

    membership = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Project member not found")

    if membership.project_role == "admin":
        raise HTTPException(status_code=400, detail="Cannot remove the project admin")

    db.delete(membership)
    db.commit()
    return {"message": "Project member removed successfully"}

@router.get("/{project_id}")
def get_project_details(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role != "admin" and not db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id).first():
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    members = db.query(User).join(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    return {"id": project.id, "name": project.name, "description": project.description, "created_by_id": project.created_by_id, "members": [{"id": member.id, "name": member.name, "email": member.email} for member in members]}

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    check_project_admin(project_id, db, current_user)

    if db.query(Issue).filter(Issue.project_id == project_id).first():
        raise HTTPException(status_code=409, detail="Cannot delete a project that contains issues")

    db.query(ProjectMember).filter(ProjectMember.project_id == project_id).delete()
    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}