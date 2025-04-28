from uuid import uuid4
from datetime import datetime
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.db.models import Document, UserDocument, DocumentChunk

class DocumentStorage:
    async def check_duplicate_document(self, content_hash: str, user_id: str, session: AsyncSession) -> bool:
        existing_doc = await session.execute(
            select(Document)
            .join(UserDocument, Document.id == UserDocument.document_id)
            .where(UserDocument.user_id == user_id)
            .where(Document.content_hash == content_hash)
        )
        return existing_doc.scalars().first() is not None

    async def store_document(self, filename: str, content_hash: str, session: AsyncSession) -> str:
        document_id = uuid4()
        await session.execute(
            insert(Document).values(
                id=document_id,
                name=filename,
                content_hash=content_hash,
                created_at=datetime.utcnow(),
            )
        )
        return document_id

    async def create_user_document_relationship(self, user_id: str, document_id: str, session: AsyncSession):
        await session.execute(
            insert(UserDocument).values(
                id=uuid4(),
                user_id=user_id,
                document_id=document_id,
                enabled_for_qa=0,
                created_at=datetime.utcnow(),
            )
        )

    async def store_chunks(self, document_id: str, chunks: list[str], embeddings: list[list[float]], session: AsyncSession):
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            await session.execute(
                insert(DocumentChunk).values(
                    id=uuid4(),
                    document_id=document_id,
                    chunk_index=idx,
                    content=chunk,
                    embedding=vector,
                    created_at=datetime.utcnow(),
                )
            )

    async def get_user_documents(self, user_id: str, session: AsyncSession):
        result = await session.execute(
            select(Document, UserDocument.enabled_for_qa)
            .join(UserDocument, Document.id == UserDocument.document_id)
            .where(UserDocument.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return result.all()

    async def toggle_document_qa(self, document_ids: list, user_id: str, session: AsyncSession):
        result = await session.execute(
            select(UserDocument)
            .where(UserDocument.document_id.in_(document_ids))
            .where(UserDocument.user_id == user_id)
        )
        user_docs = result.scalars().all()
        
        if not user_docs:
            raise HTTPException(
                status_code=404,
                detail="No documents found for the current user"
            )

        for doc in user_docs:
            await session.execute(
                update(UserDocument)
                .where(UserDocument.id == doc.id)
                .values(enabled_for_qa=1 if doc.enabled_for_qa == 0 else 0)
            )

        await session.commit()
        return {"message": "Document QA status updated successfully"}

document_storage = DocumentStorage() 