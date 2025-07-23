from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload
from app.api import query
app = FastAPI(title="Smart Research Assistant")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")