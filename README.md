# RAG Document Management System

A full-stack application for Document Management and RAG (Retrieval-Augmented Generation) based Q&A system.

## Overview

This application provides:

- Document management and storage
- RAG-based question answering
- Authentication and authorization
- Vector-based document search
- Document chunking and embedding
- Reranking of search results
- Modern React-based UI

## Architecture

The application consists of two main components:

### Frontend (`/rag-frontend`)

- React application with modern UI
- Tailwind CSS for styling
- Axios for API communication
- Nginx for serving static files

### Backend (`/rag-backend`)

- FastAPI for the web framework
- PostgreSQL with pgvector for vector storage
- Hugging Face Transformers for embeddings and reranking
- Redis for caching
- SQLAlchemy for database ORM

## Project Structure

```
rag-app/
├── rag-frontend/          # Frontend React application
│   ├── src/              # React source code
│   ├── public/           # Static assets
│   ├── Dockerfile        # Frontend container configuration
│   └── nginx.conf        # Nginx configuration
├── rag-backend/          # Backend FastAPI service
│   ├── app/             # Application code
│   ├── tests/           # Test files
│   └── Dockerfile       # Backend container configuration
├── README.md            # Main documentation
└── compose.yaml         # Docker Compose configuration
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git for version control

### Running the Application

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd rag-app
   ```

2. Start all services:
   ```bash
   docker compose up --build
   ```

This will:

- Build and start the React frontend (http://localhost:3000)
- Build and start the FastAPI backend (http://localhost:8000)
- Start PostgreSQL with pgvector (port 10000)
- Start Redis (port 6379)

### Accessing the Application

- Web Interface: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- API Base URL: http://localhost:8000
- PostgreSQL: localhost:10000
- Redis: localhost:6379

## Development

### Local Development

The code is mounted as volumes in the containers, so changes will be reflected immediately:

1. Frontend changes will trigger automatic rebuilds
2. Backend changes will reload the application
3. Database and Redis data persist across restarts

### Environment Variables

Configuration is managed through environment variables in `compose.yaml`:

```yaml
# Backend settings
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/rag_db
REDIS_HOST=redis
REDIS_PORT=6379

# Frontend settings
REACT_APP_API_URL=http://localhost:8000
```

### Testing

Run backend tests:

```bash
docker compose run backend python -m pytest
```

## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation
- SQL injection prevention
- Rate limiting

## Troubleshooting

### Common Issues

1. **Frontend Connection Issues**

   - Verify backend URL in frontend environment
   - Check CORS configuration
   - Verify network connectivity between services

2. **Backend Database Issues**

   - Ensure PostgreSQL container is running
   - Check database URL in compose.yaml
   - Verify network connectivity between containers

3. **Permission Issues**
   - Check container logs: `docker logs <container-id>`
   - Verify file permissions in volumes
   - Check user configuration in Dockerfiles

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]
