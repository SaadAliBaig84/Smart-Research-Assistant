# 📚 Smart Research Assistant

An intelligent research assistant that processes PDF documents, extracts both **text** and **images**, generates captions for visual content, and stores **multimodal embeddings** in a Supabase vector database for **semantic search** and **RAG-based Q&A**.

## 🚀 Features
- **PDF Parsing** — Extracts text, images, and metadata from PDF files (including page-wise analysis).
- **Multimodal Embeddings** — Uses CLIP (`wkcn/TinyCLIP-ViT-8M-16-Text-3M-YFCC15M`) for both text and images.
- **Image Captioning** — Generates captions for non-text PDF pages using BLIP (`Salesforce/blip-image-captioning-base`).
- **Vector Database Integration** — Stores embeddings in **Supabase** for fast similarity search.
- **Question Answering (RAG)** — Retrieves relevant document chunks and answers queries using **Groq's LLaMA 3** model.
- **LangChain Orchestration** — Manages embedding, retrieval, and prompt-based answer generation.

## 📂 Project Structure
```
Backend/
│
├── app/
│   ├── core/config.py       # API keys & environment configuration
│   ├── services/utils.py    # PDF processing utilities
│   ├── models/Embeddings/   # Embedding model wrapper
│   ├── temp.py              # Test script for PDF → Embeddings → Supabase
│
├── requirements.txt
└── README.md
```

## 🛠️ Setup
### 1️⃣ Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/Smart-Research-Assistant.git
cd Smart-Research-Assistant
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate    # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables
Create a `.env` file in the project root:
```env
HF_TOKEN=your_huggingface_token
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
GROQ_API_KEY=your_groq_api_key
```

## 📖 Usage
### Process a PDF and insert into Supabase
```python
from app.main import process_pdf

process_pdf("sample.pdf", email="user@example.com")
```

### Ask a question about your documents
```python
from app.main import get_rag_chain

retrieve, generate = get_rag_chain()
state = {"question": "What are the key findings?", "context": [], "answer": ""}

state.update(retrieve(state))
state.update(generate(state))

print("Answer:", state["answer"])
```

## 🧠 How It Works
1. **PDF Extraction**
   - Detects if a page has text, images, or both.
   - Renders non-text pages as images.
2. **Multimodal Embedding**
   - Text chunks → CLIP text encoder
   - Images → CLIP image encoder
   - Captions generated for image pages via BLIP.
3. **Supabase Vector Store**
   - Stores embeddings + metadata.
   - Supports fast similarity search.
4. **Retrieval-Augmented Generation (RAG)**
   - Retrieves top-k most relevant chunks.
   - Uses Groq LLaMA 3 for contextual Q&A.

## 📌 Notes
- Hugging Face tokens must **never** be committed to git — use `.env` files.
- Large PDFs are split into chunks for optimal search & retrieval performance.
- Image captions are approximate; for better results, a fine-tuned BLIP or Donut model can be used.

