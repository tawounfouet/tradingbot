# Troubleshooting Guide

This guide covers common issues you might encounter while installing, configuring, or running TradingBot.

## Installation Issues

### Python Version Errors

**Problem**: `ImportError` or version compatibility issues
```bash
ERROR: Python 3.11 or higher is required
```

**Solution**:
1. Check your Python version:
   ```bash
   python --version
   ```
2. Install Python 3.11+ from [python.org](https://python.org)
3. Use the correct Python executable:
   ```bash
   python3.11 -m pip install -e ".[dev,test]"
   ```

### Virtual Environment Issues

**Problem**: Package conflicts or permission errors

**Solution**:
1. Create a fresh virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   ```

### Dependencies Installation Failed

**Problem**: Some packages fail to install
```bash
ERROR: Failed building wheel for some-package
```

**Solution**:
1. Update pip and setuptools:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```
2. Install system dependencies (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install python3.11-dev build-essential
   ```
3. Install system dependencies (macOS):
   ```bash
   xcode-select --install
   brew install python@3.11
   ```

## Configuration Issues

### Environment Variables

**Problem**: Missing or incorrect environment variables

**Solution**:
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file with your configuration
3. Verify required variables are set:
   ```bash
   python -c "from tradingbot.config.settings import settings; print(settings.dict())"
   ```

### Database Connection

**Problem**: Cannot connect to database
```bash
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
```

**Solution**:
1. Check database is running:
   ```bash
   docker ps  # For Docker setups
   ```
2. Verify database URL in `.env`
3. Test connection manually:
   ```bash
   python -c "from tradingbot.database.connection import get_engine; get_engine()"
   ```

### API Keys Configuration

**Problem**: Invalid or missing API keys
```bash
binance.exceptions.BinanceAPIException: Invalid API-key
```

**Solution**:
1. Generate new API keys from your exchange
2. Update `.env` file with correct keys
3. Ensure API key permissions include:
   - Spot & Margin Trading
   - Futures Trading (if needed)
   - Read Info

## Runtime Issues

### FastAPI Server Won't Start

**Problem**: Server startup errors
```bash
uvicorn.error: Error loading ASGI app
```

**Solution**:
1. Check if port is already in use:
   ```bash
   lsof -i :8000
   ```
2. Use a different port:
   ```bash
   uvicorn tradingbot.main:app --port 8001
   ```
3. Check for import errors:
   ```bash
   python -c "from tradingbot.main import app"
   ```

### Import Errors

**Problem**: Module not found errors
```bash
ModuleNotFoundError: No module named 'tradingbot'
```

**Solution**:
1. Ensure you're in the correct virtual environment
2. Install in development mode:
   ```bash
   pip install -e .
   ```
3. Add to Python path temporarily:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

### Trading Strategy Errors

**Problem**: Strategy execution failures

**Solution**:
1. Check strategy configuration in database
2. Verify market data availability
3. Review logs for specific errors:
   ```bash
   tail -f logs/crypto_bot.log
   ```

## Docker Issues

### Build Failures

**Problem**: Docker build fails
```bash
ERROR [builder 3/8] RUN pip install -r requirements.txt
```

**Solution**:
1. Update Docker to latest version
2. Clear Docker cache:
   ```bash
   docker system prune -a
   ```
3. Build with no cache:
   ```bash
   docker-compose build --no-cache
   ```

### Container Won't Start

**Problem**: Container exits immediately

**Solution**:
1. Check logs:
   ```bash
   docker-compose logs tradingbot
   ```
2. Verify environment variables in `docker-compose.yml`
3. Check file permissions

## Performance Issues

### Slow API Responses

**Problem**: API endpoints are slow

**Solution**:
1. Check database query performance
2. Review logs for bottlenecks
3. Consider adding caching
4. Monitor resource usage:
   ```bash
   htop  # or docker stats
   ```

### Memory Usage

**Problem**: High memory consumption

**Solution**:
1. Monitor memory usage:
   ```bash
   python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
   ```
2. Reduce batch sizes in strategies
3. Implement data cleanup routines

## Development Issues

### Pre-commit Hooks Failing

**Problem**: Code quality checks fail

**Solution**:
1. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```
2. Run manually to fix issues:
   ```bash
   pre-commit run --all-files
   ```
3. Skip hooks temporarily (not recommended):
   ```bash
   git commit --no-verify
   ```

### Tests Failing

**Problem**: Unit or integration tests fail

**Solution**:
1. Run tests with verbose output:
   ```bash
   pytest -v
   ```
2. Run specific test:
   ```bash
   pytest tests/test_specific.py::test_function -v
   ```
3. Check test database setup
4. Update test fixtures if needed

## Getting Help

If you're still experiencing issues:

1. **Check the logs**: Look for error messages in `logs/crypto_bot.log`
2. **Search GitHub Issues**: Check if your issue has been reported
3. **Create an Issue**: Report bugs with:
   - Operating system and version
   - Python version
   - Error messages and stack traces
   - Steps to reproduce
4. **Join the Community**: Connect with other users for support

## Useful Commands

### Health Checks
```bash
# Check system health
python validate_setup.py

# Test database connection
python -c "from tradingbot.database.connection import test_connection; test_connection()"

# Verify API access
python -c "from tradingbot.services.market_data_service import MarketDataService; MarketDataService().get_health()"
```

### Reset and Clean Start
```bash
# Reset virtual environment
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test]"

# Reset database (caution: deletes data)
docker-compose down -v
docker-compose up -d db
```

### Development Reset
```bash
# Clean Python cache
find . -type d -name "__pycache__" -delete
find . -name "*.pyc" -delete

# Reset pre-commit
pre-commit clean
pre-commit install
```
