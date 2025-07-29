# 🚀 Crypto Trading Bot API - Complete Setup Guide

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Development Commands](#development-commands)
- [Docker Setup](#docker-setup)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Deployment](#deployment)

## 📖 Project Overview

Advanced cryptocurrency trading bot with automated strategies built with FastAPI, featuring:

- **FastAPI Backend** with async support
- **Multiple Database Support** (PostgreSQL, SQLite, MongoDB)
- **Trading Strategies Engine** with technical indicators
- **Real-time Market Data** integration
- **Secure Authentication** with JWT
- **Docker Containerization**
- **Comprehensive Testing**
- **Modern Python Development** with pyproject.toml

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Virtual environment
- Git

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd crypto-bot-api

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev,test]"
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # Update SECRET_KEY and other settings
```

### 3. Run the Application

```bash
# Using Makefile (recommended)
make run

# Or directly
cd src/tradingbot && python main.py

# Or using the startup script
./start.sh
```

### 4. Verify Installation

```bash
# Run validation script
python validate_setup.py

# Check health endpoint
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/api/v1/docs
```

## 🛠️ Development Setup

### Virtual Environment Setup

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install with all development dependencies
make install-dev
# or
pip install -e ".[dev,test,docs,ui]"
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
make pre-commit
# or
pre-commit install
```

## 📁 Project Structure

```
crypto-bot-api/
├── src/tradingbot/           # Main application code
│   ├── config/              # Configuration and settings
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── routers/             # FastAPI routes
│   ├── strategies/          # Trading strategies
│   ├── database/            # Database management
│   └── main.py             # Application entry point
├── tests/                   # Test suite
├── docker/                  # Docker configuration
├── docs/                    # Documentation
├── pyproject.toml          # Modern Python project config
├── requirements.txt        # Dependencies
├── Makefile               # Development commands
└── docker-compose.yml     # Multi-service setup
```

## ⚙️ Configuration

### Environment Variables

Key settings in `.env`:

```bash
# Security
SECRET_KEY=your-super-secret-key

# Database
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=crypto_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# API Settings
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Configuration Files

- **`pyproject.toml`** - Modern Python project configuration
- **`.env`** - Environment variables
- **`.flake8`** - Code linting configuration
- **`.pre-commit-config.yaml`** - Pre-commit hooks
- **`Makefile`** - Development commands

## 🔧 Development Commands

### Using Makefile (Recommended)

```bash
# Show all available commands
make help

# Development
make install-dev    # Install development dependencies
make run           # Start development server
make dev           # Start with auto-reload
make format        # Format code (black + isort)
make lint          # Run linting (flake8, mypy, bandit)
make test          # Run tests with coverage
make check         # Run all quality checks

# Docker
make docker-up     # Start all services
make docker-down   # Stop all services
make docker-logs   # View logs

# Utilities
make clean         # Clean cache files
make info          # Show project info
make health        # Check service health
```

### Direct Commands

```bash
# Run application
cd src/tradingbot && python main.py

# Run with uvicorn
uvicorn src.tradingbot.main:app --reload

# Run tests
pytest --cov=src

# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
bandit -r src/
```

## 🐳 Docker Setup

### Development with Docker

```bash
# Start all services (PostgreSQL, MongoDB, MinIO, App)
make docker-up

# View logs
make docker-logs

# Stop all services
make docker-down
```

### Services Included

- **crypto-bot-worker** - Main FastAPI application
- **postgres** - PostgreSQL database
- **mongo** - MongoDB for market data
- **minio** - S3-compatible object storage
- **adminer** - Database administration UI
- **mongo-express** - MongoDB administration UI

### Access Points

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Adminer**: http://localhost:8080
- **Mongo Express**: http://localhost:8081
- **MinIO Console**: http://localhost:9001

## 🧪 Testing

### Run Tests

```bash
# All tests with coverage
make test

# Specific test files
pytest tests/unit/test_auth.py

# With coverage report
pytest --cov=src --cov-report=html
```

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data
└── conftest.py    # Test configuration
```

## 🔍 Code Quality

### Linting Tools

- **flake8** - Style guide enforcement
- **black** - Code formatting
- **isort** - Import sorting
- **mypy** - Type checking
- **bandit** - Security analysis

### Pre-commit Hooks

Automatically run on every commit:
- Code formatting
- Import sorting
- Linting
- Security checks

### Configuration

All tools configured in `pyproject.toml` and supporting files.

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=your-production-secret
   ```

2. **Database Setup**
   ```bash
   # Run database migrations
   make db-upgrade
   ```

3. **Run with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Health Checks

- **Basic**: `GET /health`
- **Detailed**: `GET /health/detailed`
- **Database**: Automatic connection testing

## 📚 Additional Resources

### API Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI Spec**: http://localhost:8000/api/v1/openapi.json

### Development Tools

- **Project Validation**: `python validate_setup.py`
- **Configuration Test**: `make check`
- **Development Server**: `make dev`

### Architecture Documents

See `src/tradingbot/docs/` for detailed documentation:
- Architecture overview
- Authentication guide
- Strategies development
- Deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `make install-dev`
4. Make your changes
5. Run quality checks: `make check`
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ using FastAPI, Python 3.11+, and modern development practices.**
