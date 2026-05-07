# test_psycopg.py
import sys
import asyncio

# 🪟 КРИТИЧНО: меняем цикл событий на Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Далее ваш код...
import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings

async def test():
    print("🔌 Тест через psycopg (async)...")
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT version()"))
            print(f"✅ Подключено! PostgreSQL: {res.scalar()[:40]}...")
    finally:
        await engine.dispose()

asyncio.run(test())