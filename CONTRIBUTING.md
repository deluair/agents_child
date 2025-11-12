# Contributing to Advanced AI Agent

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (venv or conda)

### Development Setup

1. **Fork and Clone**
   ```bash
   git fork https://github.com/yourusername/advanced-ai-agent.git
   cd advanced-ai-agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .  # Install in editable mode
   ```

4. **Install Development Tools**
   ```bash
   pip install black flake8 mypy isort pytest pytest-cov pre-commit
   pre-commit install
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clear, readable code
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=agent --cov-report=html

# Run specific test file
pytest tests/unit/test_memory.py -v
```

### 4. Code Quality Checks

```bash
# Format code
black agent/ tests/
isort agent/ tests/

# Check style
flake8 agent/ tests/

# Type checking
mypy agent/

# Security check
bandit -r agent/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Maximum line length: 120 characters
- Use meaningful variable and function names

### Code Organization

```python
# Standard library imports
import os
import json
from typing import Dict, Any

# Third-party imports
import numpy as np
from loguru import logger

# Local imports
from agent.core.config import AgentConfig
```

### Documentation

- Use Google-style docstrings
- Include type hints in function signatures
- Add examples for complex functions

```python
def process_input(text: str, importance: float = 0.5) -> Dict[str, Any]:
    """
    Process input text and extract features.

    Args:
        text: Input text to process
        importance: Importance score between 0 and 1

    Returns:
        Dictionary containing processed features

    Raises:
        ValueError: If importance is out of range

    Example:
        >>> result = process_input("Hello world", importance=0.8)
        >>> print(result)
        {'text': 'Hello world', 'importance': 0.8}
    """
    if not 0.0 <= importance <= 1.0:
        raise ValueError(f"Importance must be between 0 and 1, got {importance}")

    return {"text": text, "importance": importance}
```

### Testing

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Include edge cases and error conditions

```python
def test_process_input_validation():
    """Test input validation in process_input"""
    with pytest.raises(ValueError):
        process_input("test", importance=1.5)
```

## Pull Request Process

### Before Submitting

- ✅ All tests pass
- ✅ Code is formatted (black, isort)
- ✅ Linting passes (flake8)
- ✅ Type checking passes (mypy)
- ✅ Documentation is updated
- ✅ CHANGELOG.md is updated

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

### Review Process

1. Automated checks run (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Areas for Contribution

### High Priority

- 🔴 Bug fixes
- 🔴 Security improvements
- 🔴 Performance optimizations
- 🔴 Test coverage improvements

### Medium Priority

- 🟡 New features
- 🟡 Documentation improvements
- 🟡 Example additions
- 🟡 Code refactoring

### Good First Issues

Look for issues labeled `good-first-issue` or `beginner-friendly`.

## Questions?

- **General Questions**: Open a GitHub Discussion
- **Bug Reports**: Open a GitHub Issue
- **Security Issues**: Email security@aiagent.com
- **Feature Requests**: Open a GitHub Issue with [Feature Request] tag

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- CHANGELOG.md for significant contributions
- GitHub Contributors page

Thank you for contributing! 🎉
