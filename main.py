# main.py — ПОЛНАЯ ВЕРСИЯ (FastAPI + REST + GraphQL + PostgreSQL)
# 🪟 КРИТИЧНО: фикс event loop для Windows — ДОЛЖЕН БЫТЬ ПЕРВЫМ!
import sys
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uuid
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, ForeignKey, select, update, delete
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import relationship, declarative_base
from uuid import UUID
import strawberry
from strawberry.fastapi import GraphQLRouter

# ─────────────────────────────────────────────────────
# 🔹 Конфигурация БД
DATABASE_URL = "postgresql+psycopg://postgres@localhost:5433/lab4_db"  # 👈 Порт 5433!

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()

# ─────────────────────────────────────────────────────
# 🔹 SQLAlchemy модели
class User(Base):
    __tablename__ = "users"
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")

# ─────────────────────────────────────────────────────
# 🔹 Pydantic схемы для REST
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔌 Подключение к PostgreSQL...")
    for attempt in range(5):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("БД готова, таблицы созданы!")
            break
        except Exception as e:
            print(f"БД ещё не готова. Повтор через 2с... ({attempt+1}/5)")
            import asyncio
            await asyncio.sleep(2)
    else:
        raise RuntimeError("Не удалось подключиться к БД")
    yield
    await engine.dispose()

app = FastAPI(title="User & Task API", lifespan=lifespan)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

# ─────────────────────────────────────────────────────
# REST API
#─────────────────────────────────────────────────────

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()



@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == task.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User not found")
    db_task = Task(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task))
    return result.scalars().all()

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: UUID, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Task).where(Task.id == task_id))
    await db.commit()


# ─────────────────────────────────────────────────────
# GraphQL типы (Strawberry)
# ─────────────────────────────────────────────────────

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

schema = strawberry.Schema(query=Query, mutation=Mutation)

app.include_router(GraphQLRouter(schema), prefix="/graphql")