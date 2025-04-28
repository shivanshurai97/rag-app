import pytest
import time
import asyncio
from unittest.mock import patch, MagicMock
from app.services.qa_service import qa_service
from app.core.config import settings
import numpy as np

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_qa_response_time(benchmark, test_session, mock_user_id):
    """Test the response time of the QA service."""
    question = "What is a CRM?"
    
    # Mock the document retriever to return some chunks
    with patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        
        async def query_func():
            return await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        # Run the benchmark
        result = await benchmark(query_func)
        
        # Assert that the response time is within acceptable limits
        assert benchmark.stats.stats.mean < 5.0  # Response should be under 5 seconds

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_qa_concurrent_requests(benchmark, test_session, mock_user_id):
    """Test the system's ability to handle concurrent requests."""
    questions = ["What is a CRM?", "How does CRM work?", "What are CRM features?"]
    
    # Mock the document retriever to return some chunks
    with patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        
        async def concurrent_queries():
            tasks = [
                qa_service.get_answer_for_query(q, test_session, mock_user_id)
                for q in questions
            ]
            return await asyncio.gather(*tasks)
        
        # Run the benchmark
        results = await benchmark(concurrent_queries)
        
        # Assert that all queries completed successfully
        assert len(results) == len(questions)
        assert all(isinstance(r, str) for r in results)
        assert all(len(r) > 0 for r in results)

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_qa_cache_performance(benchmark, test_session, mock_user_id):
    """Test the performance impact of caching."""
    question = "What is a CRM?"
    answer = "CRM stands for Customer Relationship Management."
    
    # Mock the document retriever to return some chunks
    with patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve, \
         patch('app.services.qa_service.db_optimizations.get_cached_answer') as mock_get_cache, \
         patch('app.services.qa_service.db_optimizations.cache_answer') as mock_cache:
        
        # First query: cache miss, retrieve from document
        mock_get_cache.return_value = None
        mock_retrieve.return_value = [answer]
        
        async def run_query():
            return await qa_service.get_answer_for_query(question, test_session, mock_user_id)
        
        # First query (cache miss)
        start_time = time.perf_counter()
        await run_query()
        first_query_time = time.perf_counter() - start_time
        
        # Second query: cache hit
        mock_get_cache.return_value = answer
        
        # Second query (cache hit)
        start_time = time.perf_counter()
        await run_query()
        second_query_time = time.perf_counter() - start_time
        
        # Assert that cached query is faster (but not necessarily 2x faster)
        assert second_query_time < first_query_time, f"Cache hit ({second_query_time:.2e}s) should be faster than cache miss ({first_query_time:.2e}s)"

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_qa_large_context_performance(benchmark, test_session, mock_user_id):
    """Test performance with large context (many chunks)."""
    # Generate a large number of chunks
    chunks = [f"CRM information chunk {i}" for i in range(50)]
    
    # Mock the document retriever to return the chunks
    with patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_retrieve.return_value = chunks
        
        async def query_with_large_context():
            return await qa_service.get_answer_for_query("What is a CRM?", test_session, mock_user_id)
        
        # Run the benchmark
        result = await benchmark(query_with_large_context)
        
        # Assert that the response time is within acceptable limits
        assert benchmark.stats.stats.mean < 10.0  # Response should be under 10 seconds for large context

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_qa_memory_usage(benchmark, test_session, mock_user_id):
    """Test memory usage during QA processing."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Mock the document retriever to return some chunks
    with patch('app.services.qa_service.document_retriever.retrieve_relevant_chunks') as mock_retrieve:
        mock_retrieve.return_value = ["CRM stands for Customer Relationship Management."]
        
        async def memory_test():
            await qa_service.get_answer_for_query("What is a CRM?", test_session, mock_user_id)
            return process.memory_info().rss / 1024 / 1024
        
        # Run the benchmark
        final_memory = await benchmark(memory_test)
        
        # Assert that memory usage is within acceptable limits
        memory_increase = final_memory - initial_memory
        assert memory_increase < 500, f"Memory increase was {memory_increase:.1f}MB, which exceeds the 500MB limit"  # Memory increase should be less than 500MB