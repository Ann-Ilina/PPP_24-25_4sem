# websocket/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.db.db import get_db
from sqlalchemy.orm import Session
from app.auth.auth import get_current_user
from app.models.models import User
import redis
import json
import asyncio
from app.core.config import settings

router = APIRouter()

try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL)
    print("Connected to Redis successfully")
except redis.ConnectionError as e:
    print(f"Failed to connect to Redis: {e}")
    raise

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await websocket.accept()
    print(f"WebSocket connected for user: {user.username}, user_id: {user.id}")

    pubsub = redis_client.pubsub()
    channel = f"ws_notifications:{user.id}"
    pubsub.subscribe(channel)
    print(f"Subscribed to Redis channel: {channel}")

    try:
        while True:
            message = pubsub.get_message(timeout=10.0)  # Увеличиваем таймаут
            if message and message["type"] == "message":
                data = message["data"].decode("utf-8")
                print(f"Received from Redis: {data}")
                await websocket.send_text(data)
            # Пинг-понг для поддержания соединения
            try:
                await websocket.send_text("ping")
                await asyncio.sleep(5)  # Пинг каждые 5 секунд
            except Exception as e:
                print(f"Ошибка пинг-понг: {e}")
                break
            await asyncio.sleep(0.1)
    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected for user: {user.username}. Код: {e.code}, Причина: {e.reason}")
    except Exception as e:
        print(f"Ошибка WebSocket: {e}")
    finally:
        pubsub.unsubscribe(channel)
        print(f"Unsubscribed from Redis channel: {channel}")