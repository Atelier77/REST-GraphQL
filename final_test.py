# final_test.py
import sys
# 🪟 КРИТИЧНО ДЛЯ WINDOWS: меняем цикл событий на совместимый
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import asyncio
import psycopg

async def main():
    print("🔌 Подключаюсь к localhost:5433 (Docker PostgreSQL)...")
    try:
        conn = await psycopg.AsyncConnection.connect(
            host="localhost",
            port=5433,        # 👈 Порт, который мы прокинули из Docker
            user="postgres",
            dbname="lab4_db",
            # password не нужен, так как в контейнере настроен trust
        )
        print("✅ Успех! Подключился к БД.")
        ver = await conn.fetchval("SELECT version()")
        print(f"🐘 Версия: {ver[:50]}...")
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())