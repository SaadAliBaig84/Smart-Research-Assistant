from fastapi import APIRouter, UploadFile, File, Form
import os
import shutil
from app.services.supabase_rag import process_pdf
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...), email:str  = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        process_pdf(file_path=
                    file_path, email=email)
        return {"message":"Pdf processed and embeddings uploaded to supabase."}
    
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        
