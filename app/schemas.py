# app/schemas.py
from typing import Annotated, Optional, List
from annotated_types import Ge, Le
from pydantic import BaseModel, constr, conint, EmailStr, ConfigDict, StringConstraints, Field
from datetime import datetime

#String 
TitleStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]
ContentStr = Annotated[str, StringConstraints(min_length=0, max_length=2000)]

#Int
UserInt = Annotated[int, Ge(1)]
ModuleInt = Annotated[int, Ge(1)]


#-------- Likes --------#
class Like(BaseModel):
    id: int
    user_id: UserInt
    post_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AddLike(BaseModel):
    user_id: UserInt
    post_id: int

#-------- Comments --------#
class Comment(BaseModel):
    id: int
    user_id: UserInt
    post_id: int
    content: ContentStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AddComment(BaseModel):
    user_id: UserInt
    post_id: int
    content: ContentStr

class UpdateComment(BaseModel):
    content: ContentStr

#-------- Main Posts stuff --------#
class Post(BaseModel):
    id: int
    post_title: TitleStr
    content: ContentStr
    user_id: UserInt = Field(..., description="User ID is required")
    module_id: int = Field(..., description="Module ID is required")
    likes: List[Like] = []
    comments: List[Comment] = []
    model_config = ConfigDict(from_attributes=True)

class AddPost(BaseModel):
    post_title: TitleStr
    content: ContentStr
    user_id: UserInt = Field(..., description="User ID is required")
    module_id: ModuleInt = Field(..., description="Module ID is required")

class UserPosts(BaseModel):
    id: int
    post_title: TitleStr
    content: ContentStr
    module_id: ModuleInt = Field(..., description="Module ID is required")
    user_id: UserInt = Field(..., description="User ID is required") # can comment out this line
    model_config = ConfigDict(from_attributes=True)

class UpdatePost(BaseModel):
    post_title: TitleStr
    content: ContentStr
    module_id: ModuleInt = Field(..., description="Module ID is required") # can comment out if needed