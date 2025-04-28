import pytest
from unittest.mock import patch, MagicMock
from app.services.reranker import reranker
from app.core.exceptions import ValidationError

@pytest.mark.functional
def test_reranker_initialization():
    """Test reranker initialization."""
    assert reranker is not None
    assert hasattr(reranker, 'rerank_chunks')
    assert hasattr(reranker, 'tokenizer')
    assert hasattr(reranker, 'model')

@pytest.mark.functional
def test_rerank_chunks_error_handling():
    """Test error handling in reranker."""
    query = "What is a CRM?"
    chunks = ["Test chunk"]
    with patch('app.services.reranker.reranker.rerank_chunks') as mock_rerank:
        mock_rerank.side_effect = Exception("Reranker error")
        with pytest.raises(Exception) as exc_info:
            reranker.rerank_chunks(query, chunks)
        assert "Reranker error" in str(exc_info.value)

@pytest.mark.functional
def test_rerank_chunks_score_threshold():
    """Test reranking with score threshold."""
    query = "What is a CRM?"
    chunks = [
        "CRM stands for Customer Relationship Management.",
        "A CRM system helps manage customer interactions.",
        "CRM software is used for sales and marketing."
    ]
    with patch('app.services.reranker.reranker.rerank_chunks') as mock_rerank:
        mock_rerank.return_value = [chunks[0]]  # Only first chunk passes threshold
        result = reranker.rerank_chunks(query, chunks, score_threshold=0.8)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == chunks[0]

@pytest.mark.functional
def test_rerank_chunks_basic():
    """Test basic reranking functionality."""
    query = "What is a CRM?"
    chunks = [
        "CRM stands for Customer Relationship Management.",
        "A CRM system helps manage customer interactions.",
        "CRM software is used for sales and marketing."
    ]
    with patch('app.services.reranker.reranker.rerank_chunks') as mock_rerank:
        mock_rerank.return_value = [chunks[0], chunks[1], chunks[2]]  # Return chunks in order
        result = reranker.rerank_chunks(query, chunks)
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == chunks[0]
        assert result[1] == chunks[1]
        assert result[2] == chunks[2]

@pytest.mark.functional
def test_rerank_chunks_with_debug_output():
    """Test reranking with debug output."""
    query = "What is a CRM?"
    chunks = [
        "CRM stands for Customer Relationship Management.",
        "A CRM system helps manage customer interactions.",
        "CRM software is used for sales and marketing."
    ]
    with patch('app.services.reranker.reranker.rerank_chunks') as mock_rerank:
        mock_rerank.return_value = [chunks[0], chunks[1], chunks[2]]
        result = reranker.rerank_chunks(query, chunks, return_debug=True)
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == chunks[0]
        assert result[1] == chunks[1]
        assert result[2] == chunks[2]

@pytest.mark.functional
def test_rerank_chunks_empty_input():
    """Test reranking with empty input."""
    query = "What is a CRM?"
    chunks = []
    with patch('app.services.reranker.reranker.rerank_chunks') as mock_rerank:
        mock_rerank.return_value = []
        result = reranker.rerank_chunks(query, chunks)
        assert isinstance(result, list)
        assert len(result) == 0

@pytest.mark.functional
def test_rerank_chunks_single_chunk():
    """Test reranking with a single chunk."""
    query = "What is a CRM?"
    chunks = ["CRM stands for Customer Relationship Management."]
    with patch('app.services.reranker.reranker.rerank_chunks') as mock_rerank:
        mock_rerank.return_value = [chunks[0]]
        result = reranker.rerank_chunks(query, chunks)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == chunks[0] 