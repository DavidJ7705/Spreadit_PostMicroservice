# app/schemas.py
from typing import Annotated, Optional, List
from annotated_types import Ge, Le
from pydantic import BaseModel, constr, conint, EmailStr, ConfigDict, StringConstraints, Field

TitleStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]
ContentStr = Annotated[str, StringConstraints(min_length=0, max_length=2000)]

class Post(BaseModel):
    id: int
    post_title: TitleStr
    content: ContentStr
    user_id: int = Field(..., description="User ID is required")
    module_id: int = Field(..., description="Module ID is required")

class AddPost(BaseModel):
    post_title: TitleStr
    content: ContentStr
    user_id: int = Field(..., description="User ID is required")
    module_id: int = Field(..., description="Module ID is required")

class UserPosts(BaseModel):
    post_title: TitleStr
    content: ContentStr
    module_id: int = Field(..., description="Module ID is required")
    user_id: int = Field(..., description="User ID is required") # can comment out this line

class UpdatePost(BaseModel):
    post_title: TitleStr
    content: ContentStr
    module_id: int = Field(..., description="Module ID is required") # can comment out if needed