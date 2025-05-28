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

# Подключаемся к Redis
redis_client = redis.Redis.from_url(settings.REDIS_URL)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await websocket.accept()
    print(f"WebSocket connected for user: {user.username}, user_id: {user.id}")

    # Подписываемся на Redis-канал для пользователя
    pubsub = redis_client.pubsub()
    channel = f"ws_notifications:{user.id}"
    pubsub.subscribe(channel)
    print(f"Subscribed to Redis channel: {channel}")

    try:
        # Запускаем асинхронный цикл для чтения сообщений из Redis
        while True:
            message = pubsub.get_message(timeout=1.0)
            if message and message["type"] == "message":
                data = message["data"].decode("utf-8")
                print(f"Received from Redis: {data}")
                await websocket.send_json(json.loads(data))
            await asyncio.sleep(0.1)  # Даём возможность другим задачам выполняться
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user.username}")
    finally:
        pubsub.unsubscribe(channel)
        redis_client.close()