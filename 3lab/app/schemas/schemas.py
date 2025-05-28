# app/schemas/schemas.py
from pydantic import BaseModel
from typing import Optional, List


# Схемы для пользователей
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


# Схемы для токена
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Новая схема для входа
class TokenRequest(BaseModel):
    username: str
    password: str


# Схемы для корпусов и поиска
class CorpusUpload(BaseModel):
    corpus_name: str
    text: str


class CorpusResponse(BaseModel):
    corpus_id: int
    message: str


class CorpusItem(BaseModel):
    id: int
    name: str


class SearchRequest(BaseModel):
    word: str
    algorithm: str
    corpus_id: int


class SearchResultItem(BaseModel):
    word: str
    distance: int


class SearchResponse(BaseModel):
    execution_time: float
    results: List[SearchResultItem]
    