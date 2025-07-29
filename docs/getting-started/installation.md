# Installation Guide

This guide will help you install and set up TradingBot on your system.

## Prerequisites

Before installing TradingBot, make sure you have the following installed:

- **Python 3.11 or higher**
- **Git**
- **Virtual environment** (recommended)

## Installation Methods

=== "🚀 Quick Install (Recommended)"

    ```bash
    # Clone the repository
    git clone https://github.com/tawounfouet/tradingbot.git
    cd tradingbot

    # Create virtual environment
    python3.11 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install with development dependencies
    pip install -e ".[dev,test]"
    ```

=== "🐳 Docker Install"

    ```bash
    # Clone the repository
    git clone https://github.com/tawounfouet/tradingbot.git
    cd tradingbot

    # Build and start with Docker
    docker-compose up --build
    ```

=== "📦 PyPI Install (Future)"

    ```bash
    # Install from PyPI (when available)
    pip install tradingbot
    ```

## Verification

After installation, verify everything is working:

```bash
# Run validation script
python validate_setup.py

# Start the development server
make run

# Check health endpoint
curl http://localhost:8000/health
```

You should see output similar to:

```json
{
  "status": "healthy",
  "timestamp": "2025-07-29T12:00:00Z",
  "version": "1.0.0"
}
```

## Dependencies

### Core Dependencies

- **FastAPI** - Modern web framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Pandas** - Data analysis
- **NumPy** - Numerical computing

### Optional Dependencies

Install additional features as needed:

```bash
# Documentation tools
pip install -e ".[docs]"

# UI components
pip install -e ".[ui]"

# All dependencies
pip install -e ".[all]"
```

## Environment Setup

### 1. Create Environment File

```bash
cp .env.example .env
```

### 2. Configure Essential Settings

Edit the `.env` file:

```env
# Security
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost/tradingbot

# Binance API (optional)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
```

### 3. Database Setup

=== "PostgreSQL (Recommended)"

    ```bash
    # Install PostgreSQL
    # macOS
    brew install postgresql

    # Ubuntu/Debian
    sudo apt-get install postgresql postgresql-contrib

    # Create database
    createdb tradingbot
    ```

=== "SQLite (Development)"

    SQLite is used automatically if PostgreSQL is not available. No additional setup required.

=== "Docker Database"

    ```bash
    # Start database services only
    docker-compose up postgres mongo
    ```

## Troubleshooting

### Common Issues

**1. Python Version**
```bash
# Check Python version
python --version

# Should be 3.11 or higher
```

**2. Permission Errors**
```bash
# Use virtual environment
python -m venv .venv
source .venv/bin/activate
```

**3. Database Connection**
```bash
# Check PostgreSQL status
pg_isready

# Or use SQLite fallback by removing DATABASE_URL from .env
```

**4. Port Already in Use**
```bash
# Change port in .env
PORT=8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](../user-guide/troubleshooting.md)
2. Review [GitHub Issues](https://github.com/tawounfouet/tradingbot/issues)
3. Create a new issue with details about your setup

## Next Steps

After installation:

1. [Quick Start Guide](quick-start.md) - Get up and running
2. [Configuration](configuration.md) - Detailed configuration options
3. [API Usage](../user-guide/api-usage.md) - Learn the API
4. [Trading Strategies](../user-guide/strategies.md) - Explore strategies
