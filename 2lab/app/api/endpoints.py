# app/api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.db import get_db
from ..cruds.cruds import create_corpus, get_corpus, get_all_corpuses  
from ..schemas.schemas import CorpusUpload, CorpusResponse, CorpusItem, SearchRequest, SearchResponse, SearchResultItem
from ..services.services import fuzzy_search
import time

router = APIRouter()

@router.post("/upload_corpus", response_model=CorpusResponse)
def upload_corpus(corpus: CorpusUpload, db: Session = Depends(get_db)):
    db_corpus = create_corpus(db, corpus.corpus_name, corpus.text)
    return CorpusResponse(corpus_id=db_corpus.id, message="Corpus uploaded successfully")

@router.get("/corpuses")
def list_corpuses(db: Session = Depends(get_db)):
    corpuses = get_all_corpuses(db)
    return {"corpuses": [CorpusItem(id=c.id, name=c.name) for c in corpuses]}

@router.post("/search_algorithm", response_model=SearchResponse)
def search_algorithm(search: SearchRequest, db: Session = Depends(get_db)):
    corpus = get_corpus(db, search.corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")
    
    start_time = time.time()
    results = fuzzy_search(search.word, corpus.text, search.algorithm)
    execution_time = time.time() - start_time
    
    return SearchResponse(
        execution_time=execution_time,
        results=[SearchResultItem(word=w, distance=d) for w, d in results[:10]]
    )