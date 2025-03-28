from pydantic import BaseModel
from typing import List, Dict, Optional


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
    algorithm: str  # "levenshtein" или "damerau-levenshtein"
    corpus_id: int


class SearchResultItem(BaseModel):
    word: str
    distance: int


class SearchResponse(BaseModel):
    execution_time: float
    results: List[SearchResultItem]

