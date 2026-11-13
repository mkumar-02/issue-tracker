from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="member", nullable=False)

    created_projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by_id")
    project_memberships = relationship("ProjectMember", back_populates="user")
    created_issues = relationship("Issue", back_populates="creator", foreign_keys="Issue.created_by_id")
    assigned_issues = relationship("Issue", back_populates="assignee", foreign_keys="Issue.assignee_id")
    comments = relationship("Comment", back_populates="author")
