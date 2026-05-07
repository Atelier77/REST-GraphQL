import socket

def test(host, port=5432):
    try:
        print(f"🔌 Проверяю {host}:{port}...")
        with socket.create_connection((host, port), timeout=5) as s:
            print("✅ Порт ОТКРЫТ! PostgreSQL отвечает.")
            return True
    except Exception as e:
        print(f"❌ Не доступно: {e}")
        return False

if __name__ == "__main__":
    test("127.0.0.1")
    test("localhost")
    test("host.docker.internal")