from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(
        default=None,
        max_length=500
    )


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_by_id: int

    model_config = {"from_attributes": True}

class ProjectMemberAdd(BaseModel):
    user_id: int