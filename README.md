# {{api-name}}

## Overview
A production-ready FastAPI project template implementing industry best practices for API development, testing, documentation, and deployment.

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI Version](https://img.shields.io/badge/FastAPI-0.95.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features
- 🚀 FastAPI with async support
- 🔐 JWT authentication with refresh tokens
- 📊 Prometheus metrics and structured logging
- 🗄️ SQLAlchemy with Alembic migrations
- 🧪 Comprehensive test suite
- 🐋 Docker and Docker Compose support
- 📝 OpenAPI documentation
- 🔍 Pre-commit hooks for code quality

## Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/your-username/hello_world_project.git
cd hello_world_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.dev.txt

# Set up environment
cp .env.dev .env

# Run migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload
```

### Docker Development
```bash
# Start services
docker-compose -f docker/docker-compose.dev.yml up -d

# Run migrations
docker-compose -f docker/docker-compose.dev.yml exec web alembic upgrade head
```

## Development Tools
- **API Documentation**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health

## Project Structure
```
.
├── src/                    # Application source code
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── db/                # Database models and migrations
│   ├── schemas/           # Pydantic models
│   └── services/          # Business logic
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                  # Documentation
├── docker/               # Docker configuration
└── scripts/              # Utility scripts
```

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test types
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

### Docker Testing
```bash
# Run migrations
docker compose -f docker/docker-compose.test.yml run --rm web pytest --cov=src
```




## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run pre-commit hooks (`pre-commit install`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Documentation
- [Development Guide](docs/development.md)
- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment_guide.md)
- [API Documentation](docs/api/endpoints.md)
- [Evolution Guide](docs/evolution_guide.md)

## Clen Repo to Use as Boilerplate

```bash
rm -rf src/api/v1/endpoints/hello.py src/services/hello.py \
tests/unit/test_hello_endpoints.py \
tests/contract/test_hello_contract.py \
tests/integration/test_hello_integration.py \
tests/e2e/test_hello_workflow.py
```	

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
