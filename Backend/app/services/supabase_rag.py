import requests

from app.services.utils import extract_text_from_pdf, chunk_text
from app.core.config import config
import os
from groq import Groq
client = Groq(api_key=config.GROQ_API_KEY)
SUPABASE_URL = config.SUPABASE_URL
SUPABASE_KEY = config.SUPABASE_SERVICE_ROLE_KEY

HEADERS={
    "apikey": SUPABASE_KEY,
    "Authorization":f"Bearer {SUPABASE_KEY}",
    "Content-Type":"application/json",
    "Prefer":"return=representation"
}

# hf_token = config.HF_TOKEN
# api_url = "https://api-inference.huggingface.co/models/BAAI/bge-small-en-v1.5"
# headers = {"Authorization": f"Bearer {hf_token}"}
api_url="https://api.together.xyz/v1/embeddings"
api_key=config.TOGETHER_API_KEY
headers = {"Authorization":f"Bearer {api_key}", "Content-Type":"application/json"}
def get_embedding(texts: list[str]) -> list[list[float]]:
    print(texts)
    response = requests.post(
        api_url,
        headers=headers,
        json={"model":"BAAI/bge-base-en-v1.5","input": texts}
    )

    print(response)
    if response.status_code != 200:
        raise Exception(f"Together AI embedding failed: {response.text}")
    data=response.json()
    embeddings = [item["embedding"] for item in data["data"]]
    print("Got embeddings for", len(embeddings), "chunks")
    return embeddings


def insert_chunk_to_supabase(chunk:str,embedding: list, source_file: str,email: str):
    payload = {
        "content": chunk,
        "embedding":embedding,
        "source_file":source_file,
        "email":email
    }
    

    response = requests.post(
        url=f"{SUPABASE_URL}/rest/v1/documents",
        headers=HEADERS,
        json=payload
    )
    if not response.ok:
        raise Exception(f"Supabase insert failed: {response.text}")
    return response.json()

def process_pdf(file_path: str, email:str):
    text = extract_text_from_pdf(file_path=file_path)
    chunks = chunk_text(text=text, chunk_size=500, overlap=50)
    embeddings = get_embedding(chunks)
    
    for chunk, embedding in zip(chunks, embeddings):
        insert_chunk_to_supabase(chunk=chunk, embedding=embedding, source_file=os.path.basename(file_path), email=email)


def search_chunks(query: str, top_k: int = 5) -> list:
    emb = get_embedding([query])[0]
    payload={
        "query_embedding":emb,
        "match_threshold":0.4,
        "match_count": top_k
    }

    response = requests.post(
        url=f"{SUPABASE_URL}/rest/v1/rpc/match_documents",
        headers=HEADERS,
        json=payload
    )

    if not response.ok:
        raise Exception(f"Supabase search failed: {response.text}")

    return response.json()

def generate_answer(query: str, context_chunks: list) -> str:
    context = "\n\n".join(chunk["content"] for chunk in context_chunks)
    prompt = f"""Answer the question based on the context provided.
    
    Question: {query}

    Context: {context}

    Answer:"""
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
        {
            "role": "user",
            "content": f"{prompt}"
        }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    return completion.choices[0].message.content.strip() if completion.choices else "No answer found."
    
