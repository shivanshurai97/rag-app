from transformers import AutoTokenizer
from app.core.config import settings
import fitz  # PyMuPDF
import os
from docx import Document
from fastapi import UploadFile
import hashlib

class DocumentProcessor:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL)

    def compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async def extract_text(self, file: UploadFile, file_ext: str) -> str:
        content = await file.read()
        if file_ext in ["txt", "md"]:
            return content.decode("utf-8")
        elif file_ext == "pdf":
            with fitz.open(stream=content, filetype="pdf") as doc:
                return "\n".join([page.get_text() for page in doc])
        elif file_ext == "docx":
            with open("temp.docx", "wb") as temp:
                temp.write(content)
            doc = Document("temp.docx")
            text = "\n".join([para.text for para in doc.paragraphs])
            os.remove("temp.docx")
            return text
        else:
            raise ValueError("Unsupported file format")

    def chunk_text_default(self, text: str, max_tokens: int = 512):
        sentences = text.split(". ")
        chunks = []
        current_chunk = []

        for sentence in sentences:
            tentative = " ".join(current_chunk + [sentence])
            token_count = len(self.tokenizer.encode(tentative, add_special_tokens=False))
            if token_count <= max_tokens:
                current_chunk.append(sentence)
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def chunk_text_overlap(self, text: str, max_tokens: int = 512, overlap: int = 128):
        words = text.split()
        step = max_tokens - overlap
        chunks = []
        for i in range(0, len(words), step):
            chunk = words[i:i + max_tokens]
            chunks.append(" ".join(chunk))
        return chunks

    def get_chunks(self, text: str) -> list[str]:
        if settings.CHUNKING_STRATEGY == "overlap":
            return self.chunk_text_overlap(text)
        elif settings.CHUNKING_STRATEGY == "paragraph":
            return [p for p in text.split("\n") if p.strip()]
        else:
            return self.chunk_text_default(text)

document_processor = DocumentProcessor() 