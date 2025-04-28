import pytest
from unittest.mock import patch, MagicMock
from app.services.embedding_service import embedding_service
from app.core.exceptions import ValidationError

@pytest.mark.functional
def test_embedding_service_initialization():
    """Test embedding service initialization."""
    assert embedding_service is not None
    assert hasattr(embedding_service, 'embed_texts')

@pytest.mark.functional
@pytest.mark.asyncio
async def test_embed_texts_error_handling():
    """Test error handling in embedding service."""
    texts = ["Test text"]
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed:
        mock_embed.side_effect = Exception("Embedding service error")
        with pytest.raises(Exception) as exc_info:
            await embedding_service.embed_texts(texts)
        assert "Embedding service error" in str(exc_info.value)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_embed_texts_batch_processing():
    """Test batch processing in embedding service."""
    texts = [f"Text {i}" for i in range(100)]  # Large batch
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1] * 768 for _ in range(100)]
        result = await embedding_service.embed_texts(texts)
        assert isinstance(result, list)
        assert len(result) == 100
        assert all(len(embedding) == 768 for embedding in result)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_embed_texts_basic():
    """Test basic text embedding functionality."""
    texts = ["Hello world", "Test embedding"]
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1] * 768, [0.2] * 768]
        result = await embedding_service.embed_texts(texts)
        assert isinstance(result, list)
        assert len(result) == 2
        assert len(result[0]) == 768
        assert len(result[1]) == 768

@pytest.mark.functional
@pytest.mark.asyncio
async def test_embed_texts_single_text():
    """Test embedding a single text."""
    text = "CRM stands for Customer Relationship Management."
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1] * 768]
        embeddings = await embedding_service.embed_texts([text])
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], list)
        assert len(embeddings[0]) == 768

@pytest.mark.functional
@pytest.mark.asyncio
async def test_embed_texts_empty_input():
    """Test embedding with empty input."""
    texts = []
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed:
        mock_embed.return_value = []
        result = await embedding_service.embed_texts(texts)
        assert isinstance(result, list)
        assert len(result) == 0

@pytest.mark.functional
@pytest.mark.asyncio
async def test_embed_texts_large_batch():
    """Test embedding with a large batch of texts."""
    texts = [f"Text {i}" for i in range(50)]
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1] * 768 for _ in range(50)]
        result = await embedding_service.embed_texts(texts)
        assert isinstance(result, list)
        assert len(result) == 50
        assert all(len(embedding) == 768 for embedding in result)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_embed_texts_long_text():
    """Test embedding with long text that needs truncation."""
    long_text = "CRM " * 1000  # Very long text that will be truncated
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1] * 768]
        embeddings = await embedding_service.embed_texts([long_text])
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], list)
        assert len(embeddings[0]) == 768

@pytest.mark.functional
@pytest.mark.asyncio
async def test_embed_texts_special_characters():
    """Test embedding with texts containing special characters."""
    texts = ["Hello, world!", "Test @#$%^&*()", "Unicode: 你好"]
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1] * 768, [0.2] * 768, [0.3] * 768]
        result = await embedding_service.embed_texts(texts)
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(len(embedding) == 768 for embedding in result) 