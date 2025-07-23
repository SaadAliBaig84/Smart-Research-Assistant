import fitz

def extract_text_from_pdf(file_path: str)-> str:
    doc = fitz.open(file_path)
    text=""
    for page in doc:
        text+=page.get_text()

    return text

def chunk_text(text:str, chunk_size:int = 500, overlap: int = 50  )-> list:
    chunks=[]
    start=0
    while start<len(text):
        end = start+chunk_size
        chunks.append(text[start:end])
        start+=chunk_size-overlap
    return chunks

