
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    JSON,
    UniqueConstraint,
    DateTime,
    func
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="member", nullable=False)

    created_projects = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by_id"
    )

    project_memberships = relationship(
        "ProjectMember",
        back_populates="user"
    )

    created_issues = relationship(
        "Issue",
        back_populates="creator",
        foreign_keys="Issue.created_by_id"
    )

    assigned_issues = relationship(
        "Issue",
        back_populates="assignee",
        foreign_keys="Issue.assignee_id"
    )

    comments = relationship(
        "Comment",
        back_populates="author"
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)


    creator = relationship(
        "User",
        back_populates="created_projects",
        foreign_keys=[created_by_id]
    )

    members = relationship(
        "ProjectMember",
        back_populates="project"
    )

    issues = relationship(
        "Issue",
        back_populates="project"
    )


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    project_role = Column(String(30), default="member", nullable=False)


    project = relationship(
        "Project",
        back_populates="members"
    )

    user = relationship(
        "User",
        back_populates="project_memberships"
    )


class Issue(Base):
    __tablename__ = "issues"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "issue_number",
            name="uq_project_issue_number"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    issue_number = Column(Integer, nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)

    priority = Column(String(20), default="medium", nullable=False)
    status = Column(String(20), default="open", nullable=False)

    labels = Column(JSON, default=list, nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)


    project = relationship(
        "Project",
        back_populates="issues"
    )

    creator = relationship(
        "User",
        back_populates="created_issues",
        foreign_keys=[created_by_id]
    )

    assignee = relationship(
        "User",
        back_populates="assigned_issues",
        foreign_keys=[assignee_id]
    )

    comments = relationship(
        "Comment",
        back_populates="issue",
        order_by="Comment.created_at"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    content = Column(String(1000), nullable=False)

    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


    issue = relationship(
        "Issue",
        back_populates="comments"
    )

    author = relationship(
        "User",
        back_populates="comments"
    )
