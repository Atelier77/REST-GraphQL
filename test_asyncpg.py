# test_asyncpg.py
import asyncio
import sys
import asyncpg

# 🪟 КРИТИЧНО ДЛЯ WINDOWS: меняем цикл событий на Selector
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    try:
        print("🔌 Подключаюсь через asyncpg (Windows Policy + ssl=False)...")
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="lab4_db",
            ssl=False,  # 🚫 Явно отключаем SSL для драйвера
            server_settings={"application_name": "lab4-test"},
        )
        print("✅ Успешно подключился!")
        print(f"🐘 PostgreSQL: {await conn.fetchval('SELECT version()')[:40]}...")
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")

asyncio.run(main())