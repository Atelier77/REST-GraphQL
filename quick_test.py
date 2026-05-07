# mini_test.py
import sys
# 🪟 Фикс Windows — ОБЯЗАТЕЛЬНО первым!
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import asyncio
import psycopg

async def main():
    print("🔌 Пробую подключиться...")
    try:
        conn = await psycopg.AsyncConnection.connect(
            host="localhost",        # 👈 Пробуем localhost вместо 127.0.0.1
            port=5432,
            user="postgres",
            dbname="lab4_db",
            # 👇 Никакого password=, так как trust
        )
        print("✅ Успех! Подключился.")
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

asyncio.run(main())