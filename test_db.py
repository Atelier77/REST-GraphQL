# test_db.py
import asyncio
import asyncpg

async def test():
    try:
        print("🔌 Пробую подключиться...")
        conn = await asyncpg.connect(
            user="postgres",
            password="postgres",
            host="host.docker.internal",
            port=5432,
            database="lab4_db",
            ssl="disable",  # 👈 КЛЮЧЕВОЙ ПАРАМЕТР
            timeout=10,
        )
        print("✅ Успешно подключился!")
        
        # Проверим, есть ли БД
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        print(f"📋 Таблицы в БД: {[t['tablename'] for t in tables]}")
        
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")

asyncio.run(test())