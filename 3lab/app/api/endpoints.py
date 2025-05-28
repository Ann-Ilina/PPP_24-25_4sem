# app/api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.db import get_db
from app.cruds.cruds import create_corpus, get_corpus, get_all_corpuses, create_user, create_token  # Добавили create_token
from app.schemas.schemas import (
    CorpusUpload, CorpusResponse, CorpusItem, SearchRequest, SearchResponse, TokenRequest,
    SearchResultItem, UserCreate, User as PydanticUser, Token
)
from app.auth.auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from app.celery.tasks import fuzzy_search_task  # Добавили задачу Celery
from datetime import datetime
from app.models.models import User as DBUser  # Alias for SQLAlchemy model

router = APIRouter()

@router.post("/register", response_model=PydanticUser)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user.username, user.password)

@router.post("/login", response_model=Token)  # Переименовали /token в /login
def login_for_access_token(user_data: TokenRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Сохраняем токен в базе данных
    expires_at = datetime.utcnow() + access_token_expires
    create_token(db, access_token, user.id, expires_at)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/upload_corpus", response_model=CorpusResponse)
def upload_corpus(corpus: CorpusUpload, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_corpus = create_corpus(db, corpus.corpus_name, corpus.text)
    return CorpusResponse(corpus_id=db_corpus.id, message="Corpus uploaded successfully")

@router.get("/corpuses")
def list_corpuses(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    corpuses = get_all_corpuses(db)
    return {"corpuses": [CorpusItem(id=c.id, name=c.name) for c in corpuses]}

@router.post("/search_algorithm")
def search_algorithm(search: SearchRequest, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    corpus = get_corpus(db, search.corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")
    
    # Запускаем задачу Celery
    task = fuzzy_search_task.delay(current_user.id, search.word, corpus.text, search.algorithm)
    return {"task_id": task.id, "message": "Search task started. Connect to WebSocket to receive updates."}