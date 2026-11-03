from pydantic import BaseModel, Field

class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: int
    content: str
    issue_id: int
    user_id: int
    model_config = {"from_attributes": True}