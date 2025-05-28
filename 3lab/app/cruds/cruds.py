# app/cruds/cruds.py
from sqlalchemy.orm import Session
from app.models.models import Corpus, User, Token  # Добавили модель Token
from app.auth.auth import get_password_hash
from datetime import datetime

def create_user(db: Session, username: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_token(db: Session, token: str, user_id: int, expires_at: datetime):
    db_token = Token(token=token, user_id=user_id, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_token(db: Session, token: str):
    return db.query(Token).filter(Token.token == token).first()

def create_corpus(db: Session, name: str, text: str):
    db_corpus = Corpus(name=name, text=text)
    db.add(db_corpus)
    db.commit()
    db.refresh(db_corpus)
    return db_corpus

def get_corpus(db: Session, corpus_id: int):
    return db.query(Corpus).filter(Corpus.id == corpus_id).first()

def get_all_corpuses(db: Session):
    return db.query(Corpus).all()