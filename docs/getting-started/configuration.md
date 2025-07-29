# Configuration Guide

This guide covers all configuration options for TradingBot.

## Environment Variables

TradingBot uses environment variables for configuration. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

### Core Settings

```env
# Security
SECRET_KEY=your-super-secret-key-here
API_PREFIX=/api/v1
ALLOWED_HOSTS=localhost,127.0.0.1

# Application
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Database Configuration

=== "PostgreSQL (Recommended)"

    ```env
    # PostgreSQL
    POSTGRES_USER=crypto_user
    POSTGRES_PASSWORD=your_secure_password
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=crypto_bot_db
    DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
    ```

=== "SQLite (Development)"

    ```env
    # SQLite (fallback)
    DATABASE_URL=sqlite:///./db.sqlite3
    ```

### External Services

```env
# Binance API
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BINANCE_TESTNET=true

# MongoDB (optional)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=crypto_bot_market_data
MONGODB_USER=mongo_user
MONGODB_PASSWORD=mongo_password

# MinIO/S3 (optional)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=tradingbot-data

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

## Configuration Classes

TradingBot uses Pydantic settings for type-safe configuration:

```python
from tradingbot.config.settings import get_settings

settings = get_settings()
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Debug mode: {settings.DEBUG}")
```

### Settings Hierarchy

1. **Environment variables** (highest priority)
2. **`.env` file**
3. **Default values** (lowest priority)

## Database Setup

### PostgreSQL Setup

=== "Docker"

    ```bash
    # Start PostgreSQL with Docker
    docker run -d \
      --name postgres-tradingbot \
      -e POSTGRES_USER=crypto_user \
      -e POSTGRES_PASSWORD=your_password \
      -e POSTGRES_DB=crypto_bot_db \
      -p 5432:5432 \
      postgres:15
    ```

=== "Local Installation"

    ```bash
    # macOS
    brew install postgresql
    brew services start postgresql

    # Ubuntu/Debian
    sudo apt-get install postgresql postgresql-contrib
    sudo systemctl start postgresql

    # Create database
    createdb crypto_bot_db
    ```

### Database Migrations

```bash
# Run migrations
make db-migrate

# Create new migration
make db-migration MESSAGE="Add new table"

# Rollback migration
make db-rollback
```

## External API Configuration

### Binance API Setup

1. **Create Binance Account**
2. **Generate API Keys**:
   - Go to API Management in your Binance account
   - Create a new API key
   - Enable "Enable Reading" and "Enable Spot & Margin Trading"
   - Restrict to specific IP addresses (recommended)

3. **Configure Environment**:
   ```env
   BINANCE_API_KEY=your_api_key_here
   BINANCE_SECRET_KEY=your_secret_key_here
   BINANCE_TESTNET=true  # Use testnet for development
   ```

### API Rate Limits

Binance API rate limits are automatically handled:

- **Weight limits**: 1200 requests per minute
- **Order limits**: 10 orders per second
- **Raw request limits**: 6000 requests per 5 minutes

## Security Configuration

### JWT Settings

```env
# JWT Configuration
SECRET_KEY=your-super-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
JWT_REFRESH_EXPIRE_DAYS=7
```

### CORS Settings

```env
# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_CREDENTIALS=true
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*
```

### Rate Limiting

```env
# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Logging Configuration

### Log Levels

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Log Files

- **Application logs**: `logs/crypto_bot.log`
- **Error logs**: `logs/error.log`
- **Access logs**: `logs/access.log`

### Structured Logging

```python
import logging
from tradingbot.config.settings import get_settings

logger = logging.getLogger(__name__)
logger.info("Strategy deployed", extra={
    "strategy_id": "moving_average",
    "symbol": "BTCUSDT",
    "user_id": 123
})
```

## Performance Configuration

### Async Settings

```env
# Async Configuration
ASYNC_POOL_SIZE=20
ASYNC_MAX_OVERFLOW=10
ASYNC_POOL_TIMEOUT=30
```

### Caching

```env
# Redis Caching
CACHE_TTL=300
CACHE_PREFIX=tradingbot:
```

## Development vs Production

### Development Settings

```env
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=*
BINANCE_TESTNET=true
```

### Production Settings

```env
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
BINANCE_TESTNET=false
SECRET_KEY=your-very-secure-production-key
```

## Configuration Validation

Run the configuration validator:

```bash
python validate_setup.py
```

This checks:
- ✅ Environment variables
- ✅ Database connectivity
- ✅ External API access
- ✅ Security settings

## Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U crypto_user -d crypto_bot_db
```

**2. Invalid Secret Key**
```bash
# Generate a secure secret key
python -c "from secrets import token_urlsafe; print(token_urlsafe(32))"
```

**3. Binance API Issues**
```bash
# Test API connectivity
curl -X GET "https://testnet.binance.vision/api/v3/ping"
```

### Debug Mode

Enable debug mode for detailed error messages:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## Configuration Examples

### Minimal Development Setup

```env
SECRET_KEY=dev-secret-key-not-for-production
DEBUG=true
```

### Full Production Setup

```env
# Security
SECRET_KEY=your-production-secret-key-32-chars-min
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:pass@db-host:5432/tradingbot

# External APIs
BINANCE_API_KEY=prod_api_key
BINANCE_SECRET_KEY=prod_secret_key
BINANCE_TESTNET=false

# Monitoring
LOG_LEVEL=WARNING
SENTRY_DSN=https://your-sentry-dsn

# Performance
ASYNC_POOL_SIZE=50
CACHE_TTL=600
```
