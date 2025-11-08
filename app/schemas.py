# app/schemas.py
from typing import Annotated, Optional, List
from annotated_types import Ge, Le
from pydantic import BaseModel, constr, conint, EmailStr, ConfigDict, StringConstraints, Field

#String 
TitleStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]
ContentStr = Annotated[str, StringConstraints(min_length=0, max_length=2000)]

#Int
UserInt = Annotated[int, Ge(1)]
ModuleInt = Annotated[int, Ge(1)]


#-------- Main Posts stuff --------#
class Post(BaseModel):
    id: int
    post_title: TitleStr
    content: ContentStr
    user_id: UserInt = Field(..., description="User ID is required")
    module_id: int = Field(..., description="Module ID is required")

class AddPost(BaseModel):
    post_title: TitleStr
    content: ContentStr
    user_id: UserInt = Field(..., description="User ID is required")
    module_id: ModuleInt = Field(..., description="Module ID is required")

class UserPosts(BaseModel):
    post_title: TitleStr
    content: ContentStr
    module_id: ModuleInt = Field(..., description="Module ID is required")
    user_id: UserInt = Field(..., description="User ID is required") # can comment out this line

class UpdatePost(BaseModel):
    post_title: TitleStr
    content: ContentStr
    module_id: ModuleInt = Field(..., description="Module ID is required") # can comment out if needed


#-------- Likes --------#
class Like(BaseModel):
    id: int
    user_id: UserInt
    post_id: int

class AddLike(BaseModel):
    user_id: UserInt
    post_id: int



#-------- Comments --------#