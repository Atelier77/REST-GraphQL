# test_pure.py
import sys
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import asyncio
import psycopg

async def test():
    print("🔌 Чистое подключение через psycopg...")
    try:
        conn = await psycopg.AsyncConnection.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            dbname="lab4_db",
            sslmode="disable",  # 👈 Явно отключаем SSL
            # 👇 Никакого password=, так как trust
        )
        print("✅ Успешно подключился!")
        ver = await conn.fetchval("SELECT version()")
        print(f"🐘 {ver[:50]}...")
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

asyncio.run(test())