from sqlalchemy.orm import Session
from ..models.models import Corpus


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
