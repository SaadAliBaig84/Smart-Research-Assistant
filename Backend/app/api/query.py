from fastapi import APIRouter, Query
from app.services.supabase_rag import search_chunks, generate_answer
from pydantic import BaseModel
router = APIRouter()
class SearchRequest(BaseModel):
    query: str
    email: str
@router.post("/search/")
async def search(request:SearchRequest):
    try:
        results = search_chunks(query=request.query)

        if not results:
            return {"message": "No results found."}
        
        print(results)
        
        answer = generate_answer(query=request.query, context_chunks=results)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}