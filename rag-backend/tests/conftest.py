import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.declarative_base import Base
from app.db.base import db
import os
import uuid
from unittest.mock import patch

# Test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/rag_test")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()

@pytest.fixture
def mock_user_id():
    """Generate a mock user ID for testing."""
    return str(uuid.uuid4())

@pytest.fixture
def mock_document_id():
    """Generate a mock document ID for testing."""
    return str(uuid.uuid4())

@pytest.fixture
def mock_chunk_id():
    """Generate a mock chunk ID for testing."""
    return str(uuid.uuid4())

@pytest.fixture(autouse=True)
def mock_services():
    """Mock all external services for testing."""
    with patch('app.services.embedding_service.embedding_service.embed_texts') as mock_embed, \
         patch('app.services.answer_generator.answer_generator.generate_answer') as mock_generate, \
         patch('app.services.reranker.reranker.rerank_chunks') as mock_rerank, \
         patch('app.services.retriever.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        # Set default return values
        mock_embed.return_value = [[0.1] * 768]  # Mock embedding vector
        mock_generate.return_value = "Test answer"
        mock_rerank.return_value = ["Test chunk 1", "Test chunk 2"]
        mock_retrieve.return_value = ["Test chunk 1", "Test chunk 2"]
        yield mock_embed, mock_generate, mock_rerank, mock_retrieve