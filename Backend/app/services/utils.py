from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import os
import fitz
def modal_check(file_path: str, page_number: int) -> dict:
    try:
        doc = fitz.open(file_path)
        if page_number < 0 or page_number >= len(doc):
            print(f"Page {page_number} does not exist in the PDF.")
            doc.close()
            return {
                "hasText": False,
                "hasImages": False,
                "hasDrawings": False,
                "isTextOnly": False
            }

        page = doc[page_number]
        text = page.get_text("text").strip()
        hasText = len(text) > 0
        images = page.get_images(full=True)
        hasImages = len(images) > 0
        drawings = page.get_drawings()
        hasDrawings = len(drawings) > 0
        isTextOnly = hasText and not hasImages and not hasDrawings

        print(f"Page {page_number}: Text={hasText}, Images={hasImages}, Drawings={hasDrawings}, TextOnly={isTextOnly}")
        doc.close()
        return {
            "hasText": hasText,
            "hasImages": hasImages,
            "hasDrawings": hasDrawings,
            "isTextOnly": isTextOnly
        }
    except Exception as e:
        print(f"Error processing page {page_number} in {file_path}: {e}")
        return {
            "hasText": False,
            "hasImages": False,
            "hasDrawings": False,
            "isTextOnly": False
        }

def extract_text_and_images_from_pdf(file_path: str, email:str) -> list[Document]:
    try:
        print(f"Attempting to load: {file_path}")
        loader = PyPDFLoader(file_path, extract_images=True)
        docs = loader.load()
        print("1 - Loaded PDF successfully")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        final_docs: list[Document] = []

        for doc in docs:
            page_number = doc.metadata.get("page",0)
            content_info = modal_check(file_path, page_number)
            doc.metadata.update({
                "email": email,
                "file_path":file_path,
                "hasText": content_info["hasText"],
                "hasImages": content_info["hasImages"],
                "hasDrawings": content_info["hasDrawings"],
                "isTextOnly": content_info["isTextOnly"]
            })
            chunks = text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                chunk_metadata = doc.metadata.copy()
                chunk_metadata["id"] = i
                final_docs.append(Document(page_content=chunk, metadata = chunk_metadata))
        print(f"2 - Processed {len(docs)} pages, created {len(final_docs)} chunks")
        return final_docs
    except Exception as e:
        print("❌ Error loading or processing PDF:", e)
        raise  # Optional: re-raise so FastAPI catches it

