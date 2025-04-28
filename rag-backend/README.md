# RAG Backend Service

A FastAPI-based backend service for Document Management and RAG (Retrieval-Augmented Generation) based Q&A system.

## Overview

This service provides:

- Document management and storage
- RAG-based question answering
- Authentication and authorization
- Vector-based document search
- Document chunking and embedding
- Reranking of search results

## Architecture

The service is built using:

- FastAPI for the web framework
- PostgreSQL with pgvector for vector storage
- Hugging Face Transformers for embeddings and reranking
- Redis for caching
- SQLAlchemy for database ORM

## Project Structure

```
rag-backend/
├── app/                    # Application code
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core functionality and configuration
│   ├── db/                # Database models and operations
│   ├── services/          # Business logic services
│   └── main.py            # Application entry point
├── tests/                 # Test files
├── Dockerfile            # Docker build configuration
├── requirements.txt      # Python dependencies
└── compose.yaml          # Docker Compose configuration
```

## Services

### Core Services

1. **Embedding Service**

   - Uses BAAI/bge-base-en-v1.5 model
   - Handles text embedding generation
   - Supports batch processing

2. **Reranker Service**

   - Uses BAAI/bge-reranker-v2-m3 model
   - Reranks search results based on relevance
   - Implements score-based filtering

3. **Document Service**

   - Handles document upload and storage
   - Manages document chunking
   - Implements vector search

4. **Q&A Service**
   - Combines retrieval and generation
   - Implements RAG pipeline
   - Handles answer generation

## API Endpoints

### Authentication

- POST /auth/signup - User registration
- POST /auth/login - User login
- POST /auth/logout - User logout
- GET /auth/validate - Validate current user session

### Documents

- POST /documents/upload - Upload document
- GET /documents/list - List user's documents
- POST /documents/select - Toggle document selection for Q&A

### RAG

- POST /rag/query - Submit question for Q&A

### Health Check

- GET /health - Check service health status


## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation
- SQL injection prevention
- Rate limiting

## Performance Considerations

- Vector search optimization
- Caching layer
- Batch processing for embeddings
- Connection pooling
- Async database operations

## Troubleshooting

### Common Issues

1. **Database Connection Issues**

   - Ensure PostgreSQL container is running
   - Check database URL in compose.yaml
   - Verify network connectivity between containers

2. **Application Startup Issues**

   - Check container logs: `docker logs <container-id>`
   - Verify all required services are healthy
   - Check environment variables

3. **Permission Issues**
   - Ensure proper file permissions
   - Check user configuration in Dockerfile
