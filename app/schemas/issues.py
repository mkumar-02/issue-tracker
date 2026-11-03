from pydantic import BaseModel, Field

class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: str = "medium"
    labels: list[str] = []

class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: str | None = None
    labels: list[str] | None = None
    status: str | None = None

class IssueResponse(BaseModel):
    id: int
    issue_number: int
    title: str
    description: str | None
    priority: str
    status: str
    labels: list[str]
    project_id: int
    created_by_id: int
    assignee_id: int | None

    model_config = {"from_attributes": True}

class IssueAssign(BaseModel):
    assignee_id: int | None