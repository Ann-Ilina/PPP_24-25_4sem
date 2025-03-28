# app/models/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    tokens = relationship("Token", back_populates="user")  # Связь с токенами

class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)  # Сам токен
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Связь с пользователем
    expires_at = Column(DateTime, nullable=False)  # Время истечения токена
    is_active = Column(Boolean, default=True)  # Статус токена (активен/отозван)
    user = relationship("User", back_populates="tokens")  # Связь с пользователем

class Corpus(Base):
    __tablename__ = "corpuses"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    text = Column(Text)