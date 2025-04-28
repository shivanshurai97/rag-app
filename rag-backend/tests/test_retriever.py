import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.retriever import document_retriever
import numpy as np
from app.core.exceptions import ValidationError

@pytest.mark.functional
def test_retriever_initialization():
    """Test retriever initialization."""
    assert document_retriever is not None
    assert hasattr(document_retriever, 'retrieve_relevant_chunks')

@pytest.mark.functional
@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_core_logic(test_session, mock_user_id):
    """Test core retrieval logic."""
    question = "What is a CRM?"
    
    # Create a mock session
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.all.return_value = [
        ("CRM stands for Customer Relationship Management.", 0.8),
        ("A CRM system helps manage customer interactions.", 0.7)
    ]
    mock_session.execute.return_value = mock_result
    
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_embed.return_value = [[0.1] * 768]
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management.", "A CRM system helps manage customer interactions."]
        
        # Test cosine distance calculation
        result = await document_retriever.retrieve_relevant_chunks(question, mock_session, mock_user_id)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(chunk, str) for chunk in result)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_user_document_filtering(test_session, mock_user_id):
    """Test user document filtering logic."""
    question = "What is a CRM?"
    
    # Create a mock session
    mock_session = AsyncMock()
    
    # Mock user documents query
    mock_user_result = AsyncMock()
    mock_user_result.all.return_value = [("doc1",), ("doc2",)]
    
    # Mock chunks query
    mock_chunks_result = AsyncMock()
    mock_chunks_result.all.return_value = [
        ("CRM stands for Customer Relationship Management.", 0.8)
    ]
    
    def execute_side_effect(*args, **kwargs):
        if "user_documents" in str(args[0]).lower():
            return mock_user_result
        return mock_chunks_result
    
    mock_session.execute.side_effect = execute_side_effect
    
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_embed.return_value = [[0.1] * 768]
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        
        result = await document_retriever.retrieve_relevant_chunks(question, mock_session, mock_user_id)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "CRM stands for Customer Relationship Management."

@pytest.mark.functional
@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_database_error(test_session, mock_user_id):
    """Test database error handling."""
    question = "What is a CRM?"
    
    # Create a mock session that raises an exception
    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("Database error")
    
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_embed.return_value = [[0.1] * 768]
        mock_retrieve.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            await document_retriever.retrieve_relevant_chunks(question, mock_session, mock_user_id)
        assert "Database error" in str(exc_info.value)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_success(test_session, mock_user_id):
    """Test successful chunk retrieval."""
    question = "What is a CRM?"
    
    # Create a mock session
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.all.return_value = [
        ("CRM stands for Customer Relationship Management.", 0.8),
        ("A CRM system helps manage customer interactions.", 0.7)
    ]
    mock_session.execute.return_value = mock_result
    
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_embed.return_value = [[0.1] * 768]
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management.", "A CRM system helps manage customer interactions."]
        result = await document_retriever.retrieve_relevant_chunks(question, mock_session, mock_user_id)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(chunk, str) for chunk in result)
        assert result[0] == "CRM stands for Customer Relationship Management."
        assert result[1] == "A CRM system helps manage customer interactions."

@pytest.mark.functional
@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_no_documents(test_session, mock_user_id):
    """Test chunk retrieval when no documents are found."""
    question = "What is a CRM?"
    
    # Create a mock session
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_embed.return_value = [[0.1] * 768]
        mock_retrieve.return_value = []
        result = await document_retriever.retrieve_relevant_chunks(question, mock_session, mock_user_id)
        assert isinstance(result, list)
        assert len(result) == 0

@pytest.mark.functional
@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_with_similarity_threshold(test_session, mock_user_id):
    """Test chunk retrieval with custom similarity threshold."""
    question = "What is a CRM?"
    
    # Create a mock session
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.all.return_value = [
        ("CRM stands for Customer Relationship Management.", 0.8),
        ("A CRM system helps manage customer interactions.", 0.2)  # Below threshold
    ]
    mock_session.execute.return_value = mock_result
    
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_embed.return_value = [[0.1] * 768]
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        result = await document_retriever.retrieve_relevant_chunks(
            question, mock_session, mock_user_id, similarity_threshold=0.5
        )
        assert isinstance(result, list)
        assert len(result) == 1  # Only one chunk should pass the threshold
        assert result[0] == "CRM stands for Customer Relationship Management."

@pytest.mark.functional
@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_error_handling(test_session, mock_user_id):
    """Test error handling during chunk retrieval."""
    question = "What is a CRM?"
    
    # Create a mock session
    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("Database error")
    
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_embed.return_value = [[0.1] * 768]
        mock_retrieve.side_effect = Exception("Database error")
        with pytest.raises(Exception) as exc_info:
            await document_retriever.retrieve_relevant_chunks(question, mock_session, mock_user_id)
        assert "Database error" in str(exc_info.value)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_with_user_documents(test_session, mock_user_id):
    """Test chunk retrieval with user-specific documents."""
    question = "What is a CRM?"
    
    # Create a mock session
    mock_session = AsyncMock()
    
    # First mock for user documents query
    mock_user_result = AsyncMock()
    mock_user_result.all.return_value = [("doc1",), ("doc2",)]
    
    # Second mock for chunks query
    mock_chunks_result = AsyncMock()
    mock_chunks_result.all.return_value = [
        ("CRM stands for Customer Relationship Management.", 0.8)
    ]
    
    # Set up the execute method to return different results based on the query
    def execute_side_effect(*args, **kwargs):
        if "user_documents" in str(args[0]).lower():
            return mock_user_result
        return mock_chunks_result
    
    mock_session.execute.side_effect = execute_side_effect
    
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_embed.return_value = [[0.1] * 768]
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        result = await document_retriever.retrieve_relevant_chunks(question, mock_session, mock_user_id)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "CRM stands for Customer Relationship Management." 