from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional, List

# 🔹 User
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase): pass
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: UUID
    class Config:
        from_attributes = True

# 🔹 Task
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: UUID

class TaskCreate(TaskBase): pass
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[UUID] = None

class TaskResponse(TaskBase):
    id: UUID
    class Config:
        from_attributes = True

# 🔹 Для GraphQL (Strawberry)
import strawberry

@strawberry.type
class GQLUser:
    id: strawberry.ID
    name: str
    email: str
    
    @strawberry.field
    async def tasks(self, info: strawberry.types.Info) -> List["GQLTask"]:
        from main import get_tasks_by_user
        return await get_tasks_by_user(info.context["db"], self.id)

@strawberry.type
class GQLTask:
    id: strawberry.ID
    title: str
    description: Optional[str]
    user_id: strawberry.ID