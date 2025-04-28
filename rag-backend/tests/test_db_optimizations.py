import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.db.optimizations import db_optimizations
from app.core.exceptions import DatabaseError
import json
import hashlib

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch('app.db.optimizations.redis_client') as mock:
        yield mock

def _get_expected_cache_key(question: str) -> str:
    """Helper function to generate expected cache key."""
    return f"qa_cache:{hashlib.md5(question.encode()).hexdigest()}"

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_cached_answer_success(mock_redis):
    """Test successful retrieval of cached answer."""
    question = "What is a CRM?"
    answer = "CRM stands for Customer Relationship Management."
    cache_key = _get_expected_cache_key(question)
    
    # Mock Redis get
    mock_redis.get.return_value = json.dumps(answer)
    
    # Create mock session
    mock_session = AsyncMock()
    
    result = await db_optimizations.get_cached_answer(question, mock_session)
    assert result == answer
    mock_redis.get.assert_called_once_with(cache_key)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_cached_answer_not_found(mock_redis):
    """Test when cached answer is not found."""
    question = "What is a CRM?"
    cache_key = _get_expected_cache_key(question)
    
    # Mock Redis get to return None
    mock_redis.get.return_value = None
    
    # Create mock session
    mock_session = AsyncMock()
    
    result = await db_optimizations.get_cached_answer(question, mock_session)
    assert result is None
    mock_redis.get.assert_called_once_with(cache_key)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_cache_answer_success(mock_redis):
    """Test successful caching of answer."""
    question = "What is a CRM?"
    answer = "CRM stands for Customer Relationship Management."
    ttl = 3600  # 1 hour
    cache_key = _get_expected_cache_key(question)
    
    # Create mock session
    mock_session = AsyncMock()
    
    await db_optimizations.cache_answer(question, answer, mock_session, ttl=ttl)
    mock_redis.setex.assert_called_once_with(
        cache_key,
        ttl,
        json.dumps(answer)
    )

@pytest.mark.functional
@pytest.mark.asyncio
async def test_cache_answer_error_handling(mock_redis):
    """Test error handling during caching."""
    question = "What is a CRM?"
    answer = "CRM stands for Customer Relationship Management."
    cache_key = _get_expected_cache_key(question)
    
    # Mock Redis to raise an exception
    mock_redis.setex.side_effect = Exception("Database error")
    
    # Create mock session
    mock_session = AsyncMock()
    
    with pytest.raises(DatabaseError) as exc_info:
        await db_optimizations.cache_answer(question, answer, mock_session)
    assert "Database error" in str(exc_info.value)
    mock_redis.setex.assert_called_once_with(cache_key, 3600, json.dumps(answer))

@pytest.mark.functional
@pytest.mark.asyncio
async def test_get_cached_answer_expired(mock_redis):
    """Test when cached answer has expired."""
    question = "What is a CRM?"
    cache_key = _get_expected_cache_key(question)
    
    # Mock Redis get to return None (expired)
    mock_redis.get.return_value = None
    
    # Create mock session
    mock_session = AsyncMock()
    
    result = await db_optimizations.get_cached_answer(question, mock_session)
    assert result is None
    mock_redis.get.assert_called_once_with(cache_key)

@pytest.mark.functional
@pytest.mark.asyncio
async def test_cache_answer_with_different_ttl(mock_redis):
    """Test caching with different TTL values."""
    question = "What is a CRM?"
    answer = "CRM stands for Customer Relationship Management."
    cache_key = _get_expected_cache_key(question)
    
    # Create mock session
    mock_session = AsyncMock()
    
    # Test with different TTL values
    for ttl in [0, 3600, 86400]:  # 0 seconds, 1 hour, 1 day
        await db_optimizations.cache_answer(question, answer, mock_session, ttl=ttl)
        mock_redis.setex.assert_called_with(
            cache_key,
            ttl,
            json.dumps(answer)
        )
        mock_redis.reset_mock()  # Reset mock for next iteration 