# Development Guide

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis
- Git

### Local Development Setup

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd rag-backend
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the project root:

   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ragdb
   REDIS_URL=redis://localhost:6379
   OPENAI_API_KEY=your_api_key
   JWT_SECRET=your_secret_key
   DEBUG=True
   ```

5. **Database Setup**

   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d db redis

   # Initialize database
   python -m app.db.base
   ```

## Code Organization

### Project Structure

```
rag-backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core functionality
│   ├── db/            # Database models
│   ├── services/      # Business logic
│   └── main.py        # Application entry
├── tests/             # Test files
└── requirements.txt   # Dependencies
```

### Coding Standards

1. **Python Style Guide**

   - Follow PEP 8
   - Use type hints
   - Document all public functions
   - Keep functions focused and small

2. **API Design**

   - Use RESTful principles
   - Version APIs appropriately
   - Document all endpoints
   - Handle errors consistently

3. **Database**
   - Use async SQLAlchemy
   - Implement proper indexing
   - Handle migrations carefully
   - Use transactions appropriately

## Development Workflow

### 1. Feature Development

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement Changes**

   - Write code
   - Add tests
   - Update documentation

3. **Run Tests**

   ```bash
   python run_tests.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: description of changes"
   ```

### 2. Code Review

1. **Create Pull Request**

   - Describe changes
   - Link related issues
   - Request reviews

2. **Address Feedback**
   - Make requested changes
   - Update documentation
   - Re-run tests

### 3. Testing

1. **Unit Tests**

   ```bash
   pytest tests/unit
   ```

2. **Integration Tests**

   ```bash
   pytest tests/integration
   ```

3. **API Tests**
   ```bash
   pytest tests/api
   ```

### 4. Documentation

1. **Code Documentation**

   - Use docstrings
   - Follow Google style
   - Include examples

2. **API Documentation**
   - Update API.md
   - Include request/response examples
   - Document error cases

## Common Tasks

### Adding a New Endpoint

1. Create route in appropriate router
2. Add request/response models
3. Implement service layer
4. Add tests
5. Update documentation

### Adding a New Service

1. Create service class
2. Implement required methods
3. Add error handling
4. Add tests
5. Update documentation

### Database Changes

1. Create migration
2. Update models
3. Test migration
4. Update documentation

## Debugging

### Logging

```python
from app.core.logger import logger

logger.info("Information message")
logger.error("Error message")
logger.debug("Debug message")
```

### Debug Mode

Set `DEBUG=True` in `.env` for detailed logs

### Common Issues

1. **Database Connection**

   - Check connection string
   - Verify database is running
   - Check network connectivity

2. **Model Loading**

   - Check model paths
   - Verify model files
   - Check memory usage

3. **API Errors**
   - Check request format
   - Verify authentication
   - Check service status

## Performance Optimization

### Database

- Use appropriate indexes
- Optimize queries
- Use connection pooling

### Caching

- Implement Redis caching
- Set appropriate TTL
- Handle cache invalidation

### Async Operations

- Use async/await properly
- Implement proper error handling
- Use background tasks when appropriate

## Deployment

### Local Deployment

```bash
docker-compose up
```

### Production Deployment

1. Build image
2. Push to registry
3. Deploy to environment

## Monitoring

### Logs

- Check application logs
- Monitor error rates
- Track performance metrics

### Health Checks

- Use /health endpoint
- Monitor service status
- Check dependencies

## Security

### Authentication

- Use JWT tokens
- Implement proper validation
- Handle token refresh

### Authorization

- Implement RBAC
- Check permissions
- Validate input

### Data Protection

- Use proper encryption
- Validate all input
- Handle sensitive data

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Create pull request

## Support

For issues and questions:

1. Check documentation
2. Search existing issues
3. Create new issue if needed
