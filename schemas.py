from typing import List, Optional
from uuid import UUID
import strawberry
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from models import User, Task
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional, List

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


import strawberry

@strawberry.type
class GQLUser:
    id: strawberry.ID
    name: str
    email: str

    @strawberry.field
    async def tasks(self) -> List["GQLTask"]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Task).where(Task.user_id == UUID(str(self.id))))
            tasks = result.scalars().all()
            return [
                GQLTask(
                    id=str(t.id),
                    title=t.title,
                    description=t.description,
                    user_id=str(t.user_id)
                )
                for t in tasks
            ]

@strawberry.type
class GQLTask:
    id: strawberry.ID
    title: str
    description: Optional[str]
    user_id: strawberry.ID

@strawberry.type
class Query:
    @strawberry.field
    async def users(self) -> List[GQLUser]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            return [GQLUser(id=str(u.id), name=u.name, email=u.email) for u in users]

    @strawberry.field
    async def user(self, id: strawberry.ID) -> Optional[GQLUser]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == UUID(str(id))))
            u = result.scalar_one_or_none()
            if u:
                return GQLUser(id=str(u.id), name=u.name, email=u.email)
            return None

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, name: str, email: str) -> GQLUser:
        async with AsyncSessionLocal() as db:
            db_user = User(name=name, email=email)
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return GQLUser(id=str(db_user.id), name=db_user.name, email=db_user.email)

    @strawberry.mutation
    async def create_task(self, title: str, description: str, user_id: strawberry.ID) -> GQLTask:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == UUID(str(user_id))))
            if not result.scalar_one_or_none():
                raise Exception("User not found")
            db_task = Task(title=title, description=description, user_id=UUID(str(user_id)))
            db.add(db_task)
            await db.commit()
            await db.refresh(db_task)
            return GQLTask(
                id=str(db_task.id),
                title=db_task.title,
                description=db_task.description,
                user_id=str(db_task.user_id)
            )