from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.models import UserDocument, Document
from app.core.exceptions import DatabaseError
import redis
import json
from typing import List, Optional
import hashlib

# Initialize Redis client for caching
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

class DatabaseOptimizations:
    async def create_optimized_indexes(self, session: AsyncSession):
        """Create optimized indexes for frequently queried columns"""
        try:
            # Create IVFFlat index for vector similarity search
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
                ON document_chunks 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """))
            
            # Create index for content hash lookups
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_content_hash 
                ON documents(content_hash);
            """))
            
            # Create index for user document relationships
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_documents_user_id 
                ON user_documents(user_id);
            """))
            
            # Create index for document chunks by document_id
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id 
                ON document_chunks(document_id);
            """))
            
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise DatabaseError(f"Failed to create indexes: {str(e)}")

    async def _get_documents_hash(self, session: AsyncSession, user_id: str) -> str:
        """Generate a hash of enabled documents for a user"""
        # Get all enabled documents for the user
        query = select(Document.id, Document.content_hash, UserDocument.enabled_for_qa)\
            .join(UserDocument, Document.id == UserDocument.document_id)\
            .where(UserDocument.user_id == user_id)\
            .where(UserDocument.enabled_for_qa == 1)  # 1 means enabled
        
        result = await session.execute(query)
        docs = result.fetchall()
        
        # Create a string of all document IDs and their hashes
        # Convert UUID to string before concatenation
        doc_string = ''.join(f"{str(doc.id)}{doc.content_hash}" for doc in docs)
        return hashlib.md5(doc_string.encode()).hexdigest()

    async def _get_cache_key(self, question: str, session: AsyncSession, user_id: Optional[str] = None) -> str:
        """Generate a unique cache key for a query that includes document state"""
        key_parts = [question]
        if user_id:
            key_parts.append(str(user_id))  # Convert UUID to string
            # Add documents hash to make cache key unique per document state
            docs_hash = await self._get_documents_hash(session, user_id)
            key_parts.append(docs_hash)
        
        return f"qa_cache:{hashlib.md5(''.join(key_parts).encode()).hexdigest()}"

    async def get_cached_answer(self, question: str, session: AsyncSession, user_id: Optional[str] = None) -> Optional[str]:
        """Get cached answer for a question"""
        try:
            cache_key = await self._get_cache_key(question, session, user_id)
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            return None
        except Exception as e:
            raise DatabaseError(f"Failed to get cached answer: {str(e)}")

    async def cache_answer(self, question: str, answer: str, session: AsyncSession, user_id: Optional[str] = None, ttl: int = 3600):
        """Cache an answer with a time-to-live"""
        try:
            cache_key = await self._get_cache_key(question, session, user_id)
            redis_client.setex(cache_key, ttl, json.dumps(answer))
        except Exception as e:
            raise DatabaseError(f"Failed to cache answer: {str(e)}")

    async def optimize_vector_search(self, session: AsyncSession):
        """Optimize vector search performance"""
        try:
            # Set the number of lists for IVFFlat index
            await session.execute(text("""
                ALTER INDEX idx_document_chunks_embedding 
                SET (lists = 100);
            """))
            
            # Set the number of probes for vector search
            await session.execute(text("""
                SET ivfflat.probes = 10;
            """))
            
            # Create a materialized view for frequently accessed documents
            await session.execute(text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS frequent_documents AS
                SELECT document_id, COUNT(*) as access_count
                FROM document_chunks
                GROUP BY document_id
                ORDER BY access_count DESC
                LIMIT 1000;
            """))
            
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise DatabaseError(f"Failed to optimize vector search: {str(e)}")

db_optimizations = DatabaseOptimizations() 