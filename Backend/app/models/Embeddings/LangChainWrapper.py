import requests
from app.core.config import config
from langchain_core.embeddings import Embeddings
from transformers import CLIPProcessor, CLIPModel, BlipForConditionalGeneration, BlipProcessor
from PIL import Image
import fitz
from langchain_core.documents import Document
class TogetherEmbeddings():
    def __init__(self):
        # self.model_name = model_name
        # self.api_key = config.TOGETHER_API_KEY
        # self.api_url = config.TOGETHER_URL
        # self.headers = {
        #     "Authorization": f"Bearer {self.api_key}",
        #     "Content-Type": "application/json"
        # }
        self.hf_key = config.HF_TOKEN
        self.model_name = "wkcn/TinyCLIP-ViT-8M-16-Text-3M-YFCC15M"
        self.model = CLIPModel.from_pretrained(self.model_name, token = self.hf_key)
        self.processor = CLIPProcessor.from_pretrained(self.model_name, token = self.hf_key)
        # Load captioning model
        self.caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    def render_page_as_image(self, pdf_path:str, page_number:int):
       doc = fitz.open(pdf_path)
       page = doc[page_number]
       pix = page.get_pixmap()
       print("hehe")
       img = Image.frombytes("RGB",[pix.width, pix.height], pix.samples)
       doc.close()
       return img
    
    def embed_documents(self, docs: list[Document]) -> list[dict]:
        results=[]
        text_emb=None
        img_emb=None
        for doc in docs:
            text_emb = None
            img_emb = None
            caption = None
            text_inputs = self.processor(text=[doc.page_content], return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77)
            text_emb = self.model.get_text_features(**text_inputs).squeeze(0).tolist()
            if not doc.metadata.get("isTextOnly", False): 
                page_number = doc.metadata.get("page",0)
                pdf_path = doc.metadata.get("file_path")
                img = self.render_page_as_image(pdf_path, page_number)
                img_inputs = self.processor(images=img, return_tensors="pt")
                img_emb = self.model.get_image_features(**img_inputs).squeeze(0).tolist()
                caption_inputs = self.caption_processor(images=img, return_tensors = "pt")
                caption = self.caption_model.generate(**caption_inputs)
                caption = self.caption_processor.decode(caption[0], skip_special_tokens=True)         
            results.append({
                "text_embedding": text_emb,
                "image_embedding": img_emb,
                "caption": caption,
                "doc": doc
            })
        return results
    def embed_query(self, text: str) -> list[float]:
        # Always process query as text
        text_inputs = self.processor(
            text=[text],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=77
        )
        return self.model.get_text_features(**text_inputs).squeeze(0).tolist()

# Initialize embedding model
