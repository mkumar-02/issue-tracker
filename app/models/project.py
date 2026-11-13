from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    creator = relationship("User", back_populates="created_projects", foreign_keys=[created_by_id])
    members = relationship("ProjectMember", back_populates="project")
    issues = relationship("Issue", back_populates="project")


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_role = Column(String(30), default="member", nullable=False)

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
