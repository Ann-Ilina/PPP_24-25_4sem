# client.py
import aiohttp
import asyncio
import json
import argparse

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"

async def get_token(username: str, password: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/login",
            json={"username": username, "password": password}
        ) as response:
            if response.status != 200:
                print(f"Ошибка авторизации: {await response.text()}")
                return None
            data = await response.json()
            return data["access_token"]

async def websocket_listener(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(WS_URL, headers=headers) as ws:
            print("Подключено к WebSocket. Ожидаем уведомления...")
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"Уведомление: {json.dumps(data, indent=2)}")
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    print("WebSocket закрыт.")
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("Ошибка WebSocket.")
                    break

async def send_search_request(token: str, word: str, corpus_id: int, algorithm: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/search_algorithm",
            json={"word": word, "corpus_id": corpus_id, "algorithm": algorithm},
            headers=headers
        ) as response:
            data = await response.json()
            print(f"Запрос отправлен: {data}")

async def interactive_mode():
    username = input("Введите имя пользователя: ")
    password = input("Введите пароль: ")
    token = await get_token(username, password)
    if not token:
        return

    ws_task = asyncio.create_task(websocket_listener(token))

    while True:
        print("\nКоманды: search, exit")
        command = input("> ").strip().lower()
        if command == "exit":
            break
        elif command == "search":
            word = input("Введите слово для поиска: ")
            corpus_id = int(input("Введите ID корпуса: "))
            algorithm = input("Введите алгоритм (например, levenshtein): ")
            await send_search_request(token, word, corpus_id, algorithm)
        else:
            print("Неизвестная команда.")

    ws_task.cancel()

async def script_mode(filename: str):
    with open(filename, "r") as f:
        lines = f.readlines()
    
    username = None
    password = None
    commands = []

    for line in lines:
        line = line.strip()
        if line.startswith("username:"):
            username = line.split(":", 1)[1].strip()
        elif line.startswith("password:"):
            password = line.split(":", 1)[1].strip()
        elif line.startswith("search:"):
            parts = line.split(":", 1)[1].strip().split(",")
            commands.append({
                "word": parts[0].strip(),
                "corpus_id": int(parts[1].strip()),
                "algorithm": parts[2].strip(),
            })

    if not username or not password:
        print("Не указаны username или password в скрипте.")
        return

    token = await get_token(username, password)
    if not token:
        return

    ws_task = asyncio.create_task(websocket_listener(token))
    for cmd in commands:
        await send_search_request(token, cmd["word"], cmd["corpus_id"], cmd["algorithm"])
        await asyncio.sleep(1)

    await ws_task

def main():
    parser = argparse.ArgumentParser(description="Консольный клиент для API")
    parser.add_argument("--script", type=str, help="Путь к файлу скрипта")
    args = parser.parse_args()

    if args.script:
        asyncio.run(script_mode(args.script))
    else:
        asyncio.run(interactive_mode())

if __name__ == "__main__":
    main()