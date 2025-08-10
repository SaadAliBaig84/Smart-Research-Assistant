import requests
from supabase import create_client
from app.services.utils import extract_text_and_images_from_pdf
from app.core.config import config
import os
from groq import Groq
from langchain.vectorstores.supabase import SupabaseVectorStore
from app.models.Embeddings.LangChainWrapper import TogetherEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnablePassthrough
from typing_extensions import TypedDict
print("SUPABASE_URL:", config.SUPABASE_URL)
print("SUPABASE_KEY:", config.SUPABASE_SERVICE_ROLE_KEY[:5] + "...")

client = Groq(api_key=config.GROQ_API_KEY)
SUPABASE_URL = config.SUPABASE_URL
SUPABASE_KEY = config.SUPABASE_SERVICE_ROLE_KEY
supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
HEADERS={
    "apikey": SUPABASE_KEY,
    "Authorization":f"Bearer {SUPABASE_KEY}",
    "Content-Type":"application/json",
    "Prefer":"return=representation"
}




# def insert_docs_to_supabase(docs: list[Document]):
#     try:
#         SupabaseVectorStore.from_documents(
#             documents=docs,
#             embedding = TogetherEmbeddings(),
#             client=supabase_client,
#             table_name="documents"
#         )
#         print("✅ Documents successfully inserted into Supabase.")
#     except Exception as e:
#         print("❌ Error inserting documents:", e)
#         raise
def process_pdf(file_path: str, email:str):
    print("1 - Extracting text & images")
    chunked_docs = extract_text_and_images_from_pdf(file_path=file_path, email=email)
    print("2 - Generating multimodal embeddings")
    embedder = TogetherEmbeddings()
    results = embedder.embed_documents(chunked_docs)
    rows=[]
    for r in results:
        rows.append({
        "content": r["doc"].page_content,
        "text_embedding": r["text_embedding"],
        "image_embedding": r["image_embedding"] if r["image_embedding"] is not None else None,
        "caption": r["caption"],
        "metadata": r["doc"].metadata
    })


    print(f"3 - Inserting {len(rows)} rows into Supabase")
    try:
        supabase_client.table("documents").insert(rows).execute()
        print("✅ Documents successfully inserted into Supabase with multimodal embeddings.")
    except Exception as e:
        print("❌ Error inserting documents:", e)
        raise
#Define application state
class State(TypedDict):
    question: str
    context: list[Document]
    answer: str

#define application steps



def get_rag_chain():
    # Initialize embedding model
    embedding = TogetherEmbeddings()

    # Supabase vector store client
    supabase = supabase_client

    # Connect to vector store
    vectorstore = SupabaseVectorStore(
        embedding=embedding,
        client=supabase,
        table_name="documents"
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Prompt template
    prompt = ChatPromptTemplate.from_template("""
        You are an intelligent assistant answering questions about a document uploaded by the user.
        Use the provided context from the document to answer the question as clearly and helpfully as possible.

        Document Context:
        {context}

        User Question:
        {question}
        """
    )

    # LLM
    llm = init_chat_model("llama3-8b-8192", model_provider="groq")

    def retrieve(state: State):
        retrieved_docs = retriever.invoke(state["question"])
        return {"context": retrieved_docs}
    
    def generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({"question":state["question"], "context":docs_content})
        response = llm.invoke(messages)
        return {"answer":response.content}
    
    return retrieve, generate


