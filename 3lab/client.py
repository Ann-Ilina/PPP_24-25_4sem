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

async def websocket_listener(token: str, queue: asyncio.Queue, stop_event: asyncio.Event):
    headers = {"Authorization": f"Bearer {token}"}
    while not stop_event.is_set():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(WS_URL, headers=headers, heartbeat=30) as ws:
                    print("Подключено к WebSocket. Ожидаем уведомления...")
                    while not stop_event.is_set() and not ws.closed:
                        try:
                            msg = await asyncio.wait_for(ws.receive(), timeout=5.0)
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = msg.data
                                if data == "ping":  # Игнорируем пинг-сообщения
                                    continue
                                try:
                                    parsed_data = json.loads(data)
                                    await queue.put(parsed_data)
                                except json.JSONDecodeError as e:
                                    print(f"Ошибка парсинга JSON: {e} для данных: '{data}'")
                            elif msg.type == aiohttp.WSMsgType.CLOSED:
                                print(f"WebSocket закрыт. Код: {ws.close_code if hasattr(ws, 'close_code') else 'Неизвестен'}")
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                print(f"Ошибка WebSocket: {ws.exception()}")
                                break
                            elif msg.type == aiohttp.WSMsgType.CLOSING:
                                print("WebSocket в процессе закрытия.")
                                break
                            else:
                                print(f"Получено сообщение неизвестного типа: {msg.type}. Пропускаем...")
                                continue  # Пропускаем неизвестные типы сообщений
                        except asyncio.TimeoutError:
                            print("Таймаут ожидания сообщения. Продолжаем...")
                        except Exception as e:
                            print(f"Ошибка при получении сообщения: {e}")
                            break
        except Exception as e:
            print(f"Ошибка соединения WebSocket: {e}. Переподключение через 2 секунды...")
            await asyncio.sleep(2)

async def send_search_request(token: str, word: str, corpus_id: int, algorithm: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/search_algorithm",
            json={"word": word, "corpus_id": corpus_id, "algorithm": algorithm},
            headers=headers
        ) as response:
            if response.status != 200:
                print(f"Ошибка поиска: {await response.text()}")
                return None
            data = await response.json()
            print(f"Запрос отправлен: {data}")
            return data

async def interactive_mode():
    username = input("Введите имя пользователя: ")
    password = input("Введите пароль: ")
    token = await get_token(username, password)
    if not token:
        return

    notification_queue = asyncio.Queue()
    stop_event = asyncio.Event()
    ws_task = asyncio.create_task(websocket_listener(token, notification_queue, stop_event))

    async def process_notifications():
        while not stop_event.is_set():
            try:
                notification = await notification_queue.get()
                print(f"Уведомление: {json.dumps(notification, indent=2)}")
            except asyncio.CancelledError:
                print("Обработка уведомлений завершена.")
                break
            except Exception as e:
                print(f"Ошибка обработки уведомлений: {e}")

    notification_task = asyncio.create_task(process_notifications())

    while True:
        print("\nКоманды: search, exit")
        command = input("> ").strip().lower()
        if command == "exit":
            stop_event.set()
            ws_task.cancel()
            notification_task.cancel()
            break
        elif command == "search":
            word = input("Введите слово для поиска: ")
            corpus_id = int(input("Введите ID корпуса: "))
            algorithm = input("Введите алгоритм (например, levenshtein): ")
            await send_search_request(token, word, corpus_id, algorithm)
        else:
            print("Неизвестная команда.")
        await asyncio.sleep(0.1)

    try:
        await ws_task
        await notification_task
    except asyncio.CancelledError:
        print("WebSocket и обработка уведомлений завершены.")

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

    notification_queue = asyncio.Queue()
    stop_event = asyncio.Event()
    ws_task = asyncio.create_task(websocket_listener(token, notification_queue, stop_event))

    async def process_notifications():
        while not stop_event.is_set():
            try:
                notification = await notification_queue.get()
                print(f"Уведомление: {json.dumps(notification, indent=2)}")
            except asyncio.CancelledError:
                print("Обработка уведомлений завершена.")
                break

    notification_task = asyncio.create_task(process_notifications())

    for cmd in commands:
        await send_search_request(token, cmd["word"], cmd["corpus_id"], cmd["algorithm"])
        await asyncio.sleep(1)

    await asyncio.sleep(2)

    stop_event.set()
    ws_task.cancel()
    notification_task.cancel()

    try:
        await ws_task
        await notification_task
    except asyncio.CancelledError:
        print("WebSocket и обработка уведомлений завершены.")

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