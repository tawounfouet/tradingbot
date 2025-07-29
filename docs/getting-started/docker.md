# Docker Setup Guide

This guide covers Docker deployment options for TradingBot.

## Quick Start with Docker

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/tawounfouet/tradingbot.git
cd tradingbot

# Start all services
docker-compose up --build
```

This starts:
- **TradingBot API** (port 8000)
- **PostgreSQL** database (port 5432)
- **MongoDB** for market data (port 27017)
- **MinIO** object storage (port 9000)
- **Adminer** database UI (port 8080)

### Option 2: Docker Only

```bash
# Build the image
docker build -t tradingbot .

# Run the container
docker run -p 8000:8000 -e SECRET_KEY=your-secret-key tradingbot
```

## Access Points

Once running, access these services:

- **API Documentation**: http://localhost:8000/api/v1/docs
- **Database Admin**: http://localhost:8080
- **MongoDB Admin**: http://localhost:8081
- **MinIO Console**: http://localhost:9001

## Configuration

### Environment Variables

Configure via `.env` file or environment variables:

```env
# Core settings
SECRET_KEY=your-secret-key
DEBUG=false
ENVIRONMENT=production

# Database
POSTGRES_HOST=postgres
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=secure_password

# External APIs
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
```

### Docker Compose Override

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'
services:
  crypto-bot-worker:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./logs:/app/logs
```

## Production Deployment

### Build for Production

```bash
# Multi-stage build for production
docker build --target production -t tradingbot:prod .

# Or use build args
docker build --build-arg BUILD_ENV=production -t tradingbot:prod .
```

### Health Checks

The Docker image includes health checks:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' container_name
```

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs crypto-bot-worker

# Check specific service
docker-compose logs postgres
```

**Database connection issues:**
```bash
# Verify database is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U crypto_user -d crypto_bot_db
```

**Port conflicts:**
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Change host port
```
