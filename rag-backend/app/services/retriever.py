import numpy as np
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import DocumentChunk, UserDocument
from app.services.embedding_service import embedding_service
from app.core.logger import logger

class DocumentRetriever:
    async def retrieve_relevant_chunks(
        self,
        question: str,
        session: AsyncSession,
        user_id: Optional[str] = None,
        similarity_threshold: float = 0.3
    ) -> List[str]:
        logger.info(f"Starting chunk retrieval for question: {question}")
        
        try:
            # Step 1: Embed the question
            logger.info("Generating question embedding")
            question_embedding = (await embedding_service.embed_texts([question]))[0]
            embedding_vector = np.array(question_embedding).tolist()
            logger.info("Question embedding generated successfully")

            # Step 2: Use pgvector to filter by similarity
            cosine_distance = DocumentChunk.embedding.cosine_distance(embedding_vector)
            similarity_expr = (1 - cosine_distance) * 100

            chunks_query = select(
                DocumentChunk.content,  # Only select the content field
                similarity_expr.label("similarity_percent")
            ).where(
                cosine_distance <= similarity_threshold
            ).order_by(
                similarity_expr.desc()
            )

            if user_id:
                logger.info(f"Fetching enabled documents for user: {user_id}")
                # Get documents enabled for QA for this user
                try:
                    result = await session.execute(
                        select(UserDocument.document_id)
                        .where(
                            UserDocument.user_id == user_id,
                            UserDocument.enabled_for_qa == 1
                        )
                    )
                    selected_doc_ids = [str(row[0]) for row in result.all()]  # Convert UUIDs to strings
                    logger.info(f"Found {len(selected_doc_ids)} enabled documents")
                    
                    if not selected_doc_ids:
                        logger.warning("No documents enabled for QA")
                        return []  # Return empty list if no documents are enabled for QA
                        
                    chunks_query = chunks_query.where(DocumentChunk.document_id.in_(selected_doc_ids))
                except Exception as e:
                    logger.error(f"Error fetching enabled documents: {str(e)}")
                    raise

            logger.info("Executing final chunks query")
            try:
                result = await session.execute(chunks_query)
                filtered_chunks = result.all()
                chunk_count = len(filtered_chunks)
                logger.info(f"Retrieved {chunk_count} relevant chunks")
                
                chunks = [chunk.content for chunk in filtered_chunks]  # Access content directly
                return chunks
            except Exception as e:
                logger.error(f"Error executing chunks query: {str(e)}")
                raise
                
        except Exception as e:
            logger.error(f"Unexpected error in chunk retrieval: {str(e)}")
            raise

document_retriever = DocumentRetriever() 