# Development Guide

## Version
1.0.1

## Last Updated
2025-02-10

## Overview
This guide outlines development standards and practices for the **{{ project_name }}** codebase.  
It serves as the primary reference for developers working on the project.

## Table of Contents
1. [Development Environment](#development-environment)  
2. [Code Organization](#code-organization)  
3. [Coding Standards](#coding-standards)  
4. [Testing Guidelines](#testing-guidelines)  
5. [Version Control](#version-control)  
6. [Documentation](#documentation)  

---

## Development Environment

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 16
- Git

### IDE Configuration
Recommended VS Code settings:
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "files.trimTrailingWhitespace": true
}
```

### Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
.\venv\Scripts\activate  # On Windows

pip install -r requirements.dev.txt
```

---

## Code Organization

### Directory Structure
```plaintext
{{ project_name }}/
├── src/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── schemas/
│   ├── services/
├── docs/
├── docker/
│   ├── docker-compose.prod.yml
│   ├── docker-compose.dev.yml
│   ├── docker-compose.test.yml
│   ├── Dockerfile.prod
│   ├── Dockerfile.dev
│   ├── Dockerfile.test
├── migrations/
│   ├── versions/
│   ├── env.py
├── tests/
│   ├── contract/
│   ├── performance/
│   ├── property_based/
│   ├── unit/
│   ├── integration/
│   ├── __init__.py
│   ├── conftest.py
├── scripts/
│   ├── db/
│   ├── migrations/
│   ├── tests/
│   ├── utils/
├── .gitignore
├── .pre-commit-config.yaml
├── .vscode/
├── .env.test
├── .env.dev
├── .env.prod
├── requirements.dev.txt
├── requirements.prod.txt
├── requirements.test.txt
├── pyproject.toml
├── README.md
├── CHANGELOG.md
```

### File Naming Conventions
- Use lowercase.
- Use underscores for separation.
- Be descriptive but concise.
- Follow the “one thing, one file” principle.

### Module Organization
```python
"""
Module docstring explaining purpose.
"""

# Standard library imports
import os
import sys

# Third-party imports
import fastapi
import sqlalchemy

# Local application imports
from src.core import config
from src.utils import logging

# Constants
MAX_RETRIES = 3

# Classes
class MyClass:
    """Class docstring."""
    pass

# Functions
def my_function():
    """Function docstring."""
    pass

# Main execution
if __name__ == "__main__":
    my_function()
```

---

## Coding Standards

### Python Style
- [PEP 8](https://peps.python.org/pep-0008/): Style Guide for Python Code  
- [PEP 257](https://peps.python.org/pep-0257/): Docstring Conventions  
- [PEP 484](https://peps.python.org/pep-0484/): Type Hints  
- [PEP 526](https://peps.python.org/pep-0526/): Syntax for Variable Annotations  
- [PEP 561](https://peps.python.org/pep-0561/): Packaging and Distributing Type Information  
- [PEP 544](https://peps.python.org/pep-0544/): Protocols (for advanced type-checking)  
- [PEP 570](https://peps.python.org/pep-0570/): Positional-Only Parameters (can be relevant for advanced type usage)  
- Use type hints throughout.  
- Maximum line length: 88 characters.  
- Use descriptive variable names.

### FastAPI Best Practices
- Use dependency injection.  
- Implement proper error handling.  
- Use Pydantic models for validation.  
- Implement proper response models.  
- Use routers to structure endpoints when appropriate.

### Database Practices
- Use SQLAlchemy models.  
- Implement proper migrations.  
- Use database transactions.  
- Handle connection pooling.

---

## Testing Guidelines

### Test Types

1. **Unit Tests**  
   - Test individual components.  
   - Use pytest fixtures.  
   - Mock external dependencies.

2. **Integration Tests**  
   - Test component interactions.  
   - Use a test database.  
   - Reset state between tests.

3. **End-to-End Tests**  
   - Test complete workflows.  
   - Use a production-like environment.  
   - Clean up test data.

4. **Performance Tests**  
   - Test under load.  
   - Measure response times.  
   - Check resource usage.

5. **Contract Tests** (if relevant)  
   - Validate contracts with external services.  
   - Ensure backward compatibility between versions.

6. **Property-Based Tests** (if relevant)  
   - Use randomly generated inputs.  
   - Check if the code holds for all valid inputs.

### Test Writing Standards
```python
def test_feature():
    """
    GIVEN: Initial conditions
    WHEN: Action is performed
    THEN: Expected outcome
    """
    # Test implementation
```

---

## Version Control

### Branch Strategy
- **main**: Production code  
- **develop**: Development code  
- **feature/\***: New features  
- **bugfix/\***: Bug fixes  
- **release/\***: Release preparation

### Commit Messages
```
type(scope): Brief description

Detailed description if needed

Fixes #123
```

### Pull Requests
- Use a PR template.  
- Include tests.  
- Update documentation.  
- Add migration scripts if needed.

---

## Documentation

### Code Documentation
- Use docstrings for all modules, classes, and functions.  
- Include type hints to clarify function parameters and return types.  
- Document exceptions that might be raised.  
- Add usage examples where appropriate.

### API Documentation
- Update OpenAPI specs automatically or manually as needed.  
- Include request/response examples.  
- Document error responses.  
- Mention any rate limits or authentication requirements.

### Changelog
- Keep `CHANGELOG.md` updated.  
- Follow semantic versioning.  
- Include migration notes when relevant.
