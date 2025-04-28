# RAG Application Frontend

A modern React-based frontend for the Document Management and RAG Q&A system.

## Features

- Modern, responsive UI built with React and Tailwind CSS
- Document upload and management interface
- Interactive Q&A system with RAG capabilities
- Real-time search with vector similarity
- User authentication and profile management
- Document preview and annotation tools

## Tech Stack

- React 18+
- Tailwind CSS for styling
- Axios for API communication
- Nginx for production serving
- Docker for containerization

## Project Structure

```
rag-frontend/
├── src/                # Source code
│   ├── api/           # API integration layer
│   ├── components/    # Reusable UI components
│   ├── contexts/      # React contexts
│   ├── hooks/         # Custom React hooks
│   ├── pages/         # Page components
│   ├── styles/        # Global styles and Tailwind config
│   └── utils/         # Utility functions
├── public/            # Static assets
├── Dockerfile         # Container configuration
├── nginx.conf         # Nginx server configuration
└── package.json       # Dependencies and scripts
```

## Development Setup

### Prerequisites

- Node.js 20.x or higher
- npm 9.x or higher
- Docker (optional, for containerized development)

### Local Development

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create a `.env` file:

   ```env
   REACT_APP_API_URL=http://localhost:8000
   ```

3. Start development server:
   ```bash
   npm start
   ```

The application will be available at http://localhost:3000

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

### Docker Development

Build and run using Docker:

```bash
docker build -t rag-frontend .
docker run -p 3000:80 rag-frontend
```

Or use Docker Compose from the root directory:

```bash
docker compose up frontend
```

## Available Scripts

- `npm start` - Runs development server
- `npm test` - Runs test suite
- `npm run build` - Creates production build
- `npm run lint` - Runs ESLint
- `npm run format` - Formats code with Prettier

## Environment Variables

| Variable          | Description     | Default               |
| ----------------- | --------------- | --------------------- |
| REACT_APP_API_URL | Backend API URL | http://localhost:8000 |

## Code Style

- ESLint for code linting
- Prettier for code formatting
- Husky for pre-commit hooks
```

## Deployment

The application is containerized and can be deployed using the provided Dockerfile. The production build is served using Nginx.

### Nginx Configuration

The `nginx.conf` file includes:

- Gzip compression
- Cache control headers
- SPA routing support
- Security headers

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **API Connection Errors**

   - Verify REACT_APP_API_URL is set correctly
   - Check if backend is running
   - Verify CORS configuration

2. **Build Issues**

   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules: `rm -rf node_modules`
   - Reinstall dependencies: `npm install`

3. **Development Server Issues**
   - Check port conflicts
   - Verify Node.js version
   - Clear browser cache
