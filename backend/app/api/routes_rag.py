from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.pipeline import answer_query, build_index, index_status

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


@router.get("/rag/status")
def rag_status():
    return index_status()


@router.post("/rag/build")
def rag_build(force: bool = False):
    return build_index(force=force)


@router.post("/rag/query")
def rag_query(req: QueryRequest):
    return answer_query(req.question, top_k=req.top_k)
