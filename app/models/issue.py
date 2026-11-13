from sqlalchemy import Column, Integer, String, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (UniqueConstraint("project_id", "issue_number", name="uq_project_issue_number"),)

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

    project = relationship("Project", back_populates="issues")
    creator = relationship("User", back_populates="created_issues", foreign_keys=[created_by_id])
    assignee = relationship("User", back_populates="assigned_issues", foreign_keys=[assignee_id])
    comments = relationship("Comment", back_populates="issue", order_by="Comment.created_at")
