
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Project, ProjectMember, User, Issue
from app.schemas.projects import ProjectCreate, ProjectMemberAdd


def check_project_admin(project_id: int, db: Session, current_user: User):
    if current_user.role == "admin":
        return

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if not membership or membership.project_role != "admin":
        raise HTTPException(status_code=403, detail="Project admin access required")


def create_project(db: Session, project_data: ProjectCreate, current_admin: User):
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        created_by_id=current_admin.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    membership = ProjectMember(
        project_id=new_project.id,
        user_id=current_admin.id,
        project_role="admin"
    )

    db.add(membership)
    db.commit()

    return new_project


def get_my_projects(db: Session, current_user: User):
    return db.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()


def add_project_member(db: Session, project_id: int, member_data: ProjectMemberAdd, current_user: User):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    check_project_admin(project_id, db, current_user)

    user = db.query(User).filter(User.id == member_data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="User is already a project member")

    membership = ProjectMember(
        project_id=project_id,
        user_id=user.id,
        project_role="member"
    )

    db.add(membership)
    db.commit()

    return {"message": "Project member added successfully"}


def remove_project_member(db: Session, project_id: int, user_id: int, current_user: User):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    check_project_admin(project_id, db, current_user)

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Project member not found")

    if membership.project_role == "admin":
        raise HTTPException(status_code=400, detail="Cannot remove the project admin")

    db.delete(membership)
    db.commit()

    return {"message": "Project member removed successfully"}


def get_project_details(db: Session, project_id: int, current_user: User):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role != "admin" and not db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first():
        raise HTTPException(status_code=403, detail="You are not a member of this project")

    members = db.query(User).join(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_by_id": project.created_by_id,
        "members": [
            {"id": member.id, "name": member.name, "email": member.email}
            for member in members
        ]
    }


def delete_project(db: Session, project_id: int, current_user: User):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    check_project_admin(project_id, db, current_user)

    if db.query(Issue).filter(Issue.project_id == project_id).first():
        raise HTTPException(status_code=409, detail="Cannot delete a project that contains issues")

    db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).delete()

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}
