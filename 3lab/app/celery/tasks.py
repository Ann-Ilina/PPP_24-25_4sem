# app/celery/tasks.py
from celery import Celery
from app.core.config import settings
from app.services.services import fuzzy_search
import time
import json
import redis

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.celery.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
)

# Подключаемся к Redis для публикации сообщений
redis_client = redis.Redis.from_url(settings.REDIS_URL)

def send_ws_notification(user_id: int, message: dict):
    # Публикуем сообщение в Redis-канал
    channel = f"ws_notifications:{user_id}"
    redis_client.publish(channel, json.dumps(message))
    print(f"Published to Redis channel {channel}: {message}")

@celery_app.task(bind=True)
def fuzzy_search_task(self, user_id: int, word: str, text: str, algorithm: str):
    print(f"Task started: {self.request.id}, user_id: {user_id}, word: {word}, algorithm: {algorithm}")
    
    start_message = {
        "status": "STARTED",
        "task_id": self.request.id,
        "word": word,
        "algorithm": algorithm,
    }
    send_ws_notification(user_id, start_message)

    words = text.split()
    total_words = len(words)
    results = []

    for i, current_word in enumerate(words):
        time.sleep(0.1)
        if (i + 1) % 10 == 0 or i == total_words - 1:
            progress = int(((i + 1) / total_words) * 100)
            progress_message = {
                "status": "PROGRESS",
                "task_id": self.request.id,
                "progress": progress,
                "current_word": f"processing word {i + 1}/{total_words}",
            }
            send_ws_notification(user_id, progress_message)

    start_time = time.time()
    results = fuzzy_search(word, text, algorithm)
    execution_time = time.time() - start_time

    result_message = {
        "status": "COMPLETED",
        "task_id": self.request.id,
        "execution_time": execution_time,
        "results": [
            {"word": w, "distance": d} for w, d in results[:10]
        ],
    }
    send_ws_notification(user_id, result_message)

    return result_message