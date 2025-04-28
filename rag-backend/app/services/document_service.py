from uuid import uuid4
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
import fitz  # PyMuPDF
import hashlib
from transformers import AutoTokenizer
import os
from docx import Document
from app.core.config import settings
from app.db.models import Document, UserDocument, DocumentChunk
from app.services.embedding_service import embedding_service
from app.services.document_processor import document_processor
from app.services.document_storage import document_storage
from app.core.exceptions import (
    ValidationError,
    ConflictError,
    DatabaseError,
    FileError,
    NotFoundError
)
from typing import List

class DocumentService:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL)

    def compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async def process_and_store_document(self, file: UploadFile, session: AsyncSession, current_user):
        try:
            # Validate file
            if not file.filename:
                raise ValidationError("No file provided")
            
            file_ext = file.filename.split(".")[-1].lower()
            if file_ext not in settings.supported_file_types:
                raise ValidationError(f"Unsupported file type. Supported types: {', '.join(settings.supported_file_types)}")
            
            # Check file size
            file_size = 0
            for chunk in file.file:
                file_size += len(chunk)
                if file_size > settings.MAX_DOCUMENT_SIZE:
                    raise ValidationError(f"File size exceeds maximum limit of {settings.MAX_DOCUMENT_SIZE} bytes")
            await file.seek(0)  # Reset file pointer
            
            # Extract text from document
            try:
                raw_text = await document_processor.extract_text(file, file_ext)
            except Exception as e:
                raise FileError(f"Error extracting text from document: {str(e)}")
                
            content_hash = document_processor.compute_hash(raw_text)

            # Check for duplicates
            if await document_storage.check_duplicate_document(content_hash, current_user.id, session):
                raise ConflictError("This document has already been uploaded")

            # Get chunks from text
            try:
                chunks = document_processor.get_chunks(raw_text)
                if not chunks:
                    raise ValidationError("Document is empty or could not be processed")
            except Exception as e:
                raise FileError(f"Error processing document chunks: {str(e)}")

            # Get embeddings for chunks
            try:
                embeddings = await embedding_service.embed_texts(chunks)
            except Exception as e:
                raise DatabaseError(f"Error generating embeddings: {str(e)}")

            # Store document and get document_id
            try:
                document_id = await document_storage.store_document(file.filename, content_hash, session)
            except Exception as e:
                raise DatabaseError(f"Error storing document: {str(e)}")

            # Create user-document relationship
            try:
                await document_storage.create_user_document_relationship(current_user.id, document_id, session)
            except Exception as e:
                raise DatabaseError(f"Error creating document relationship: {str(e)}")

            # Store chunks with embeddings
            try:
                await document_storage.store_chunks(document_id, chunks, embeddings, session)
            except Exception as e:
                raise DatabaseError(f"Error storing document chunks: {str(e)}")

            await session.commit()
            return {"document_id": document_id, "chunks": len(chunks)}
            
        except (ValidationError, ConflictError, FileError, DatabaseError):
            raise
        except Exception as e:
            raise DatabaseError(f"Unexpected error processing document: {str(e)}")

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

    async def get_user_documents(self, session: AsyncSession, user_id: str) -> List[Document]:
        try:
            result = await session.execute(
                select(Document, UserDocument.enabled_for_qa)
                .join(UserDocument, Document.id == UserDocument.document_id)
                .where(UserDocument.user_id == user_id)
                .order_by(Document.created_at.desc())
            )
            documents = []
            for doc, enabled in result.all():
                documents.append({
                    "id": doc.id,
                    "name": doc.name,
                    "created_at": doc.created_at,
                    "enabled_for_qa": enabled
                })
            return documents
        except Exception as e:
            raise DatabaseError(f"Error fetching documents: {str(e)}")

    async def toggle_document_qa(self, document_ids: list, user_id: str, session: AsyncSession):
        try:
            if not document_ids:
                raise ValidationError("No documents selected")
                
            # Verify all documents belong to the user
            result = await session.execute(
                select(UserDocument).where(
                    UserDocument.user_id == user_id,
                    UserDocument.document_id.in_(document_ids)
                )
            )
            user_documents = result.scalars().all()
            
            if len(user_documents) != len(document_ids):
                raise ValidationError("One or more documents do not belong to the user")
                
            # Toggle QA status
            for user_doc in user_documents:
                user_doc.enabled_for_qa = 1 if user_doc.enabled_for_qa == 0 else 0
                
            await session.commit()
            return {"message": "Document QA status updated successfully"}
            
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Error toggling document QA status: {str(e)}")

document_service = DocumentService() 