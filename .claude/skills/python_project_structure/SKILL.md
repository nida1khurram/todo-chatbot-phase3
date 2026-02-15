---
name: python_project_structure
description: Set up Python 3.13+ project with UV package manager, create pyproject.toml with dependencies, initialize src/ directory structure with __init__.py files, and set up tests/ directory.
---

# Python Project Structure Skill

You are an expert at setting up modern Python projects using Python 3.13+ and UV package manager following best practices.

## When to Use This Skill

Apply this skill when the user:
- Starts a new Python project
- Asks to "set up Python project" or "initialize Python"
- Needs UV package manager configuration
- Wants modern Python project structure with src layout
- Needs to configure pyproject.toml

## Target Structure

The complete Python project structure:

```
project-name/
├── pyproject.toml              # Project configuration & dependencies
├── uv.lock                     # UV lock file (auto-generated)
├── .python-version             # Python version specification
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore patterns
├── .env.example                # Environment variable template
├── src/
│   └── project_name/           # Main package (snake_case)
│       ├── __init__.py         # Package initialization
│       ├── main.py             # Entry point
│       ├── cli.py              # CLI interface (if applicable)
│       ├── config.py           # Configuration management
│       ├── models/             # Data models
│       │   └── __init__.py
│       ├── services/           # Business logic
│       │   └── __init__.py
│       └── utils/              # Utility functions
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   │   └── __init__.py
│   └── integration/            # Integration tests
│       └── __init__.py
└── scripts/                    # Development scripts
    └── setup.sh
```

## Setup Process

### 1. Prerequisites Check

Verify UV is installed:

```bash
# Check UV installation
uv --version || echo "UV not installed - install with: curl -LsSf https://astral.sh/uv/install.sh | sh"

# Check Python version
python3 --version
```

### 2. Initialize Project with UV

```bash
# Create new project directory
mkdir -p [project-name]
cd [project-name]

# Initialize UV project
uv init

# Set Python version
echo "3.13" > .python-version

# Create virtual environment with specific Python version
uv venv --python 3.13
```

### 3. Create pyproject.toml

```toml
[project]
name = "[project-name]"
version = "0.1.0"
description = "[Project description]"
readme = "README.md"
requires-python = ">=3.13"
license = { text = "MIT" }
authors = [
    { name = "[Author Name]", email = "[email]" }
]
keywords = ["[keyword1]", "[keyword2]"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
]

dependencies = [
    "pydantic>=2.0",
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.23",
    "mypy>=1.8",
    "ruff>=0.3",
    "pre-commit>=3.6",
]

[project.scripts]
[project-name] = "[project_name].main:main"

[project.urls]
Homepage = "https://github.com/[username]/[project-name]"
Repository = "https://github.com/[username]/[project-name]"
Issues = "https://github.com/[username]/[project-name]/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/[project_name]"]

[tool.ruff]
target-version = "py313"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
]
ignore = [
    "E501",   # line too long (handled by formatter)
    "B008",   # do not perform function calls in argument defaults
]

[tool.ruff.lint.isort]
known-first-party = ["[project_name]"]

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_configs = true
show_error_codes = true
files = ["src", "tests"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "-ra",
]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["src"]
branch = true
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### 4. Create Directory Structure

```bash
# Create src layout
mkdir -p src/[project_name]/{models,services,utils}

# Create test directories
mkdir -p tests/{unit,integration}

# Create scripts directory
mkdir -p scripts
```

### 5. Create __init__.py Files

Create `src/[project_name]/__init__.py`:

```python
"""[Project Name] - [Brief description]."""

__version__ = "0.1.0"
__all__ = ["__version__"]
```

Create `src/[project_name]/models/__init__.py`:

```python
"""Data models for [project_name]."""

__all__: list[str] = []
```

Create `src/[project_name]/services/__init__.py`:

```python
"""Business logic services for [project_name]."""

__all__: list[str] = []
```

Create `src/[project_name]/utils/__init__.py`:

```python
"""Utility functions for [project_name]."""

__all__: list[str] = []
```

Create `tests/__init__.py`:

```python
"""Test suite for [project_name]."""
```

Create `tests/unit/__init__.py` and `tests/integration/__init__.py`:

```python
"""[Unit/Integration] tests for [project_name]."""
```

### 6. Create Main Entry Point

Create `src/[project_name]/main.py`:

```python
"""Main entry point for [project_name]."""

from rich.console import Console

console = Console()


def main() -> None:
    """Run the main application."""
    console.print("[bold green]Hello from [project_name]![/bold green]")


if __name__ == "__main__":
    main()
```

### 7. Create Configuration Module

Create `src/[project_name]/config.py`:

```python
"""Configuration management for [project_name]."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = "[project_name]"
    debug: bool = False
    log_level: str = "INFO"


settings = Settings()
```

### 8. Create Test Configuration

Create `tests/conftest.py`:

```python
"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_data() -> dict[str, str]:
    """Provide sample test data."""
    return {"key": "value"}
```

Create `tests/unit/test_main.py`:

```python
"""Unit tests for main module."""

from [project_name].main import main


def test_main_runs_without_error() -> None:
    """Test that main function executes without raising exceptions."""
    # Should not raise any exception
    main()
```

### 9. Create .gitignore

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# UV
.venv/
uv.lock

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Environments
.env
.env.local
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# ruff
.ruff_cache/

# OS
.DS_Store
Thumbs.db
```

### 10. Create .env.example

```bash
# Application Configuration
APP_NAME=[project_name]
DEBUG=false
LOG_LEVEL=INFO

# Database (if applicable)
# DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# API Keys (if applicable)
# API_KEY=your-api-key-here
```

### 11. Install Dependencies

```bash
# Install all dependencies including dev
uv sync --all-extras

# Or install just production dependencies
uv sync

# Add a new dependency
uv add [package-name]

# Add a dev dependency
uv add --dev [package-name]
```

### 12. Verify Setup

```bash
# Run the application
uv run python -m [project_name].main

# Or using the script entry point
uv run [project-name]

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run type checking
uv run mypy src tests

# Run linting
uv run ruff check src tests

# Format code
uv run ruff format src tests
```

## Common UV Commands

| Command | Description |
|---------|-------------|
| `uv init` | Initialize new project |
| `uv venv` | Create virtual environment |
| `uv sync` | Install dependencies from pyproject.toml |
| `uv add <pkg>` | Add production dependency |
| `uv add --dev <pkg>` | Add development dependency |
| `uv remove <pkg>` | Remove dependency |
| `uv run <cmd>` | Run command in venv |
| `uv lock` | Update lock file |
| `uv pip list` | List installed packages |

## Python 3.13+ Features to Use

### Type Parameter Syntax (PEP 695)

```python
# Old way
from typing import TypeVar
T = TypeVar("T")
def first[T](items: list[T]) -> T: ...

# Python 3.13+ way
def first[T](items: list[T]) -> T:
    return items[0]
```

### Improved Error Messages

Python 3.13 provides better error messages - leverage them in development.

### Pattern Matching (3.10+)

```python
match command:
    case {"action": "create", "name": name}:
        create_item(name)
    case {"action": "delete", "id": id}:
        delete_item(id)
    case _:
        raise ValueError("Unknown command")
```

## Validation Checklist

```markdown
## Python Project Setup Checklist

### Structure
- [ ] pyproject.toml created with correct configuration
- [ ] .python-version specifies Python 3.13
- [ ] src/[project_name]/ directory created
- [ ] All __init__.py files in place
- [ ] tests/ directory with conftest.py
- [ ] .gitignore configured

### Dependencies
- [ ] UV initialized and working
- [ ] Production dependencies listed
- [ ] Dev dependencies listed (pytest, mypy, ruff)
- [ ] uv.lock generated

### Configuration
- [ ] Ruff configured for linting and formatting
- [ ] Mypy configured with strict mode
- [ ] Pytest configured with sensible defaults
- [ ] Coverage configured

### Verification
- [ ] `uv run python -m [project_name].main` works
- [ ] `uv run pytest` passes
- [ ] `uv run mypy src` passes
- [ ] `uv run ruff check src` passes
```

## Troubleshooting

### UV Not Found

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell or source profile
source ~/.bashrc  # or ~/.zshrc
```

### Python Version Issues

```bash
# List available Python versions
uv python list

# Install specific Python version
uv python install 3.13

# Create venv with specific version
uv venv --python 3.13
```

### Import Errors

Ensure src layout is properly configured:

```bash
# Install in editable mode
uv pip install -e .

# Or run with uv run which handles this
uv run python -m [project_name].main
```
