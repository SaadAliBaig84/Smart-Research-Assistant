from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.supabase_rag import get_rag_chain, State
from langgraph.graph import START, StateGraph 
router = APIRouter()
class SearchRequest(BaseModel):
    query: str
    email: str
retrieve_node, generate_node = get_rag_chain()
graph_builder = StateGraph(State).add_sequence([retrieve_node, generate_node])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()
@router.post("/search/")
async def search(request:SearchRequest):
    try:
        response = graph.invoke({"question":request.query})
        return {"answer": response["answer"]}
    except Exception as e:
        return {"error": str(e)}