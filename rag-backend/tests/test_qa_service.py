import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.qa_service import qa_service
from app.core.exceptions import ValidationError, DatabaseError
import numpy as np

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_success(test_session, mock_user_id, mock_services):
    """Test successful answer generation with valid input."""
    question = "What is a CRM?"
    
    # Mock the document retriever to return some chunks
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache, \
         patch('app.services.qa_service.db_optimizations.cache_answer') as mock_cache_answer, \
         patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve, \
         patch('app.services.qa_service.answer_generator.generate_answer') as mock_generate:
        
        # Set up mocks
        mock_cache.return_value = None  # No cache hit
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        mock_generate.return_value = "Test answer"
        
        # Call the service
        answer = await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        # Verify the answer
        assert answer is not None
        assert isinstance(answer, str)
        assert len(answer) > 0
        
        # Verify the mocks were called correctly
        mock_cache.assert_called_once_with(question, test_session, mock_user_id)
        mock_cache_answer.assert_called_once()
        mock_retrieve.assert_called_once_with(question, test_session, mock_user_id)
        mock_generate.assert_called_once()

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_no_chunks(test_session, mock_user_id, mock_services):
    """Test behavior when no relevant chunks are found."""
    question = "What is a CRM?"
    
    # Get the mocks from the mock_services fixture
    mock_embed, mock_generate, mock_rerank, mock_retrieve = mock_services
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache:
        # Set up mocks
        mock_cache.return_value = None  # No cache hit
        mock_retrieve.return_value = []  # Override the fixture's default return value
        
        # Call the service
        answer = await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        # Verify the answer
        expected_message = "No relevant documents found for your question. Please try rephrasing or upload relevant documents first or enable the uploaded documents for QA."
        assert answer == expected_message
        mock_retrieve.assert_called_once_with(question, test_session, mock_user_id)
        mock_cache.assert_called_once_with(question, test_session, mock_user_id)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_empty_question(test_session, mock_user_id, mock_services):
    """Test behavior with empty question input."""
    question = ""
    
    with pytest.raises(ValidationError) as exc_info:
        await qa_service.get_answer_for_query(question, test_session, mock_user_id)
    
    assert "Question must not be empty" in str(exc_info.value)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_cache_hit(test_session, mock_user_id, mock_services):
    """Test behavior when answer is found in cache."""
    question = "What is a CRM?"
    cached_answer = "CRM stands for Customer Relationship Management."
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache:
        # Set up mock
        mock_cache.return_value = cached_answer
        
        # Call the service
        answer = await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        # Verify the answer
        assert answer == cached_answer
        mock_cache.assert_called_once_with(question, test_session, mock_user_id)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_reranking(test_session, mock_user_id, mock_services):
    """Test behavior when reranking is enabled."""
    question = "What is a CRM?"
    chunks = [f"CRM chunk {i}" for i in range(15)]  # More than 10 chunks to trigger reranking
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache, \
         patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve, \
         patch('app.services.qa_service.reranker.rerank_chunks') as mock_rerank, \
         patch('app.services.qa_service.answer_generator.generate_answer') as mock_generate:
        
        # Set up mocks
        mock_cache.return_value = None
        mock_retrieve.return_value = chunks
        mock_rerank.return_value = chunks[:10]  # Return top 10 chunks
        mock_generate.return_value = "Test answer"
        
        # Call the service
        answer = await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        # Verify the answer and mocks
        assert answer is not None
        mock_rerank.assert_called_once_with(question, chunks, score_threshold=0.0, return_debug=True)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_no_reranking(test_session, mock_user_id, mock_services):
    """Test behavior when reranking is disabled."""
    question = "What is a CRM?"
    chunks = [f"CRM chunk {i}" for i in range(5)]  # Less than 10 chunks, no reranking
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache, \
         patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve, \
         patch('app.services.qa_service.reranker.rerank_chunks') as mock_rerank, \
         patch('app.services.qa_service.answer_generator.generate_answer') as mock_generate:
        
        # Set up mocks
        mock_cache.return_value = None
        mock_retrieve.return_value = chunks
        mock_generate.return_value = "Test answer"
        
        # Call the service
        answer = await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        # Verify the answer and mocks
        assert answer is not None
        mock_rerank.assert_not_called()

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_reranking_error(test_session, mock_user_id, mock_services):
    """Test behavior when reranking fails."""
    question = "What is a CRM?"
    chunks = [f"CRM chunk {i}" for i in range(15)]  # More than 10 chunks to trigger reranking
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache, \
         patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve, \
         patch('app.services.qa_service.reranker.rerank_chunks') as mock_rerank:
        
        # Set up mocks
        mock_cache.return_value = None
        mock_retrieve.return_value = chunks
        mock_rerank.side_effect = Exception("Reranking failed")
        
        with pytest.raises(Exception) as exc_info:
            await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        assert "Reranking failed" in str(exc_info.value)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_cache_error(test_session, mock_user_id, mock_services):
    """Test behavior when cache check fails."""
    question = "What is a CRM?"
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache, \
         patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        
        # Set up mocks
        mock_cache.side_effect = Exception("Cache error")
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        
        # Should continue execution even if cache fails
        answer = await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        assert answer is not None
        assert isinstance(answer, str)
        assert len(answer) > 0

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_answer_generation_error(test_session, mock_user_id, mock_services):
    """Test behavior when answer generation fails."""
    question = "What is a CRM?"
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache, \
         patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve, \
         patch('app.services.qa_service.answer_generator.generate_answer') as mock_generate:
        
        # Set up mocks
        mock_cache.return_value = None
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        mock_generate.side_effect = Exception("Answer generation failed")
        
        with pytest.raises(ValidationError) as exc_info:
            await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        assert "Failed to generate answer" in str(exc_info.value)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_cache_storage_error(test_session, mock_user_id, mock_services):
    """Test behavior when storing to cache fails."""
    question = "What is a CRM?"
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache, \
         patch('app.services.qa_service.db_optimizations.cache_answer') as mock_cache_answer, \
         patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        
        # Set up mocks
        mock_cache.return_value = None
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        mock_cache_answer.side_effect = Exception("Cache storage failed")
        
        # Should still return answer even if cache storage fails
        answer = await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        assert answer is not None
        assert isinstance(answer, str)
        assert len(answer) > 0

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_answer_for_query_reranking_no_chunks_passed(test_session, mock_user_id, mock_services):
    """Test behavior when reranking filters out all chunks."""
    question = "What is a CRM?"
    chunks = [f"CRM chunk {i}" for i in range(15)]  # More than 10 chunks to trigger reranking
    
    with patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_cache, \
         patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve, \
         patch('app.services.qa_service.reranker.rerank_chunks') as mock_rerank:
        
        # Set up mocks
        mock_cache.return_value = None
        mock_retrieve.return_value = chunks
        mock_rerank.return_value = []  # Reranking filters out all chunks
        
        answer = await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        expected_message = "No highly relevant content found to answer your question accurately. Please try rephrasing or upload more relevant documents."
        assert answer == expected_message 