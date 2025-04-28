# API Documentation

## Authentication Endpoints

### Sign Up

- **Endpoint**: `POST /auth/signup`
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Response**: User details with HTTP-only cookie set

### Login

- **Endpoint**: `POST /auth/login`
- **Description**: Authenticate user
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: User details with HTTP-only cookie set

### Logout

- **Endpoint**: `POST /auth/logout`
- **Description**: Log out current user
- **Response**: Success message with cookie cleared

### Validate Session

- **Endpoint**: `GET /auth/validate`
- **Description**: Validate current user session
- **Response**: Current user details

## Document Management

### Upload Document

- **Endpoint**: `POST /documents/upload`
- **Description**: Upload and process a document
- **Request Body**: Form data with file
- **Response**: Document details

### List Documents

- **Endpoint**: `GET /documents/list`
- **Description**: Get list of user's documents
- **Response**: Array of document objects

### Toggle Document Selection

- **Endpoint**: `POST /documents/select`
- **Description**: Toggle document selection for Q&A
- **Request Body**:
  ```json
  {
    "document_id": "string",
    "is_selected": boolean
  }
  ```
- **Response**: Updated document details

## RAG Q&A

### Submit Question

- **Endpoint**: `POST /rag/query`
- **Description**: Submit a question for Q&A
- **Request Body**:
  ```json
  {
    "question": "string"
  }
  ```
- **Response**: Answer with sources

## Health Check

### Service Health

- **Endpoint**: `GET /health`
- **Description**: Check service health status
- **Response**:
  ```json
  {
    "status": "healthy",
    "version": "string",
    "app_name": "string",
    "database": "string",
    "services": {
      "embedding": "string",
      "reranker": "string"
    }
  }
  ```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a message and details:

```json
{
  "detail": "Error message",
  "status_code": number
}
```
