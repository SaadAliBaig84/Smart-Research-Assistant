import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-supabase-url.supabase.co")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-service-role-key")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "your-hf_token")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "your-groq-api-key")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "your-google-api-key")
    TOGETHER_API_KEY: str = os.getenv("TOGETHER_API_KEY", "your-together-api-key")
    TOGETHER_URL: str = os.getenv("TOGETHER_URL","")

config = Config()

# Initialize Supabase client


