from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import openai
from app.core.config import settings
from app.services.retriever import document_retriever
from app.services.reranker import reranker
from app.services.answer_generator import answer_generator
from app.core.exceptions import ValidationError, DatabaseError, NotFoundError
from app.db.optimizations import db_optimizations
from app.core.logger import logger

class QAService:
    def __init__(self):
        try:
            self.reranker_tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3')
            self.reranker_model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3')
            self.reranker_model.eval()
            openai.api_key = settings.OPENAI_API_KEY
        except Exception as e:
            raise ValidationError(f"Failed to initialize RAG service: {str(e)}")

    def rerank_chunks(self, question: str, chunks: List[str], score_threshold: float = 1.0, return_debug: bool = False) -> List[str]:
        if not question or not chunks:
            raise ValidationError("Question and chunks must not be empty")
            
        try:
            pairs = [[question, chunk] for chunk in chunks]
            with torch.no_grad():
                inputs = self.reranker_tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
                scores = self.reranker_model(**inputs, return_dict=True).logits.view(-1).float()

            # Filter and sort by score
            scored_pairs = sorted(
                [(score.item(), chunk) for score, chunk in zip(scores, chunks) if score.item() >= score_threshold],
                key=lambda x: x[0],
                reverse=True
            )

            if return_debug:
                print("🔍 Reranker Scores:")
                for score, chunk in scored_pairs:
                    print(f"Score: {score:.2f} | Chunk: {chunk[:80]}...")

            return [chunk for _, chunk in scored_pairs]
        except Exception as e:
            raise ValidationError(f"Failed to rerank chunks: {str(e)}")

    async def get_answer_for_query(self, question: str, session: AsyncSession, user_id: Optional[str] = None) -> str:
        logger.info(f"Processing query: {question} for user: {user_id}")
        
        if not question:
            logger.error("Empty question received")
            raise ValidationError("Question must not be empty")
            
        try:
            # Check cache first
            logger.info("Checking cache for existing answer")
            try:
                cached_answer = await db_optimizations.get_cached_answer(question, session, user_id)
                if cached_answer:
                    logger.info("Cache hit - returning cached answer")
                    return cached_answer
            except Exception as e:
                logger.error(f"Cache check failed: {str(e)}")
                # Continue execution even if cache fails

            # Step 1: Retrieve relevant chunks
            logger.info("Retrieving relevant chunks")
            try:
                chunk_texts = await document_retriever.retrieve_relevant_chunks(question, session, user_id)
                logger.info(f"Retrieved {len(chunk_texts)} chunks")
            except Exception as e:
                logger.error(f"Chunk retrieval failed: {str(e)}")
                raise

            if not chunk_texts:
                logger.warning("No relevant chunks found")
                return "No relevant documents found for your question. Please try rephrasing or upload relevant documents first or enable the uploaded documents for QA."

            # Step 2: Rerank chunks only if we have more than 10 chunks
            if len(chunk_texts) > 10:
                logger.info("More than 10 chunks found, using reranker")
                try:
                    reranked_chunks = reranker.rerank_chunks(question, chunk_texts, score_threshold=0.0, return_debug=True)
                    logger.info(f"Reranked chunks count: {len(reranked_chunks)}")
                    if not reranked_chunks:
                        logger.warning("No chunks passed reranking threshold")
                        return "No highly relevant content found to answer your question accurately. Please try rephrasing or upload more relevant documents."
                    # Use top 10 reranked chunks
                    top_chunks = reranked_chunks[:10]
                except Exception as e:
                    logger.error(f"Reranking failed: {str(e)}")
                    raise
            else:
                logger.info("10 or fewer chunks found, using all chunks directly")
                top_chunks = chunk_texts

            # Step 3: Build context from chunks
            context = "\n".join(top_chunks)
            logger.info(f"Built context from {len(top_chunks)} chunks")

            # Step 4: Generate answer
            try:
                logger.info("Generating answer")
                answer = answer_generator.generate_answer(question, context)
                
                # Cache the answer
                logger.info("Caching the generated answer")
                try:
                    await db_optimizations.cache_answer(question, answer, session, user_id, settings.CACHE_TTL)
                except Exception as e:
                    logger.error(f"Failed to cache answer: {str(e)}")
                    # Continue even if caching fails
                
                return answer
            except Exception as e:
                logger.error(f"Answer generation failed: {str(e)}")
                raise ValidationError(f"Failed to generate answer: {str(e)}")
                
        except (NotFoundError, ValidationError) as e:
            logger.error(f"Known error occurred: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in QA process: {str(e)}")
            raise DatabaseError(f"Failed to process query: {str(e)}")

qa_service = QAService() 