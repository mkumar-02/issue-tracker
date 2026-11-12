from sqlalchemy.orm import Session
from app.schemas.projects import ProjectMemberAdd

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User
from app.schemas.projects import ProjectCreate, ProjectMemberAdd, ProjectResponse
from app.core.security import get_current_admin, get_current_user
from app.services.project_service import (
    create_project,
    get_my_projects,
    add_project_member,
    remove_project_member,
    get_project_details,
    delete_project
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(project_data: ProjectCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return create_project(db, project_data, current_admin)


@router.get("/", response_model=list[ProjectResponse])
def get_my_projects_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_my_projects(db, current_user)


@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
def add_project_member_endpoint(project_id: int, member_data: ProjectMemberAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return add_project_member(db, project_id, member_data, current_user)


@router.delete("/{project_id}/members/{user_id}")
def remove_project_member_endpoint(project_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return remove_project_member(db, project_id, user_id, current_user)


@router.get("/{project_id}")
def get_project_details_endpoint(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_project_details(db, project_id, current_user)


@router.delete("/{project_id}")
def delete_project_endpoint(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return delete_project(db, project_id, current_user)
