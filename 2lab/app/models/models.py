from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Corpus(Base):
    __tablename__ = "corpuses"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    text = Column(Text)
