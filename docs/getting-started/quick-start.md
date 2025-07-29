# Quick Start Guide

Get TradingBot up and running in minutes with this quick start guide.

## 🚀 5-Minute Setup

### Step 1: Clone and Install

```bash
git clone https://github.com/tawounfouet/tradingbot.git
cd tradingbot
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test]"
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your preferred editor:

```env
SECRET_KEY=your-secret-key-here
DEBUG=true
ENVIRONMENT=development
```

### Step 3: Start the Application

```bash
make run
```

### Step 4: Verify Installation

Open your browser and navigate to:

- **API Documentation**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health

## 📊 First API Request

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-29T12:00:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

### 2. Get Available Strategies

```bash
curl http://localhost:8000/api/v1/strategies
```

Expected response:
```json
[
  {
    "id": "moving_average_crossover",
    "name": "Moving Average Crossover",
    "description": "Trend-following strategy using fast and slow moving averages",
    "status": "active"
  },
  {
    "id": "rsi_reversal",
    "name": "RSI Reversal",
    "description": "Mean reversion strategy based on RSI indicator",
    "status": "active"
  }
]
```

## 🔐 Authentication Flow

### 1. Create a User Account

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "trader1",
       "email": "trader1@example.com",
       "password": "SecurePassword123!",
       "full_name": "John Trader"
     }'
```

### 2. Login and Get Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "trader1",
       "password": "SecurePassword123!"
     }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "trader1",
    "email": "trader1@example.com"
  }
}
```

### 3. Make Authenticated Requests

```bash
# Store token
TOKEN="eyJhbGciOiJIUzI1NiIs..."

# Get user profile
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/users/me"
```

## 🤖 Deploy Your First Strategy

### 1. Create Strategy Configuration

```bash
curl -X POST "http://localhost:8000/api/v1/strategies/deploy" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "strategy_id": "moving_average_crossover",
       "symbol": "BTCUSDT",
       "parameters": {
         "fast_period": 10,
         "slow_period": 20,
         "position_size": 0.1
       },
       "risk_management": {
         "max_position_size": 1000,
         "stop_loss_percentage": 2.0,
         "take_profit_percentage": 4.0
       }
     }'
```

### 2. Monitor Strategy Status

```bash
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/strategies/deployments"
```

### 3. View Performance

```bash
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/strategies/deployments/1/performance"
```

## 📈 Run a Backtest

### 1. Start Backtest

```bash
curl -X POST "http://localhost:8000/api/v1/backtest/run" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "strategy_id": "moving_average_crossover",
       "symbol": "BTCUSDT",
       "start_date": "2024-01-01",
       "end_date": "2024-12-31",
       "initial_capital": 10000,
       "parameters": {
         "fast_period": 10,
         "slow_period": 20
       }
     }'
```

### 2. Check Results

```bash
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/backtest/results/1"
```

Response:
```json
{
  "id": 1,
  "strategy_id": "moving_average_crossover",
  "symbol": "BTCUSDT",
  "performance": {
    "total_return": 15.25,
    "annual_return": 12.34,
    "max_drawdown": -8.45,
    "sharpe_ratio": 1.45,
    "total_trades": 156,
    "win_rate": 0.67
  },
  "status": "completed"
}
```

## 🐳 Docker Quick Start

### 1. Start All Services

```bash
docker-compose up --build
```

This starts:
- TradingBot API (port 8000)
- PostgreSQL database (port 5432)
- MongoDB (port 27017)
- MinIO object storage (port 9000)
- Adminer database UI (port 8080)

### 2. Access Services

- **API Docs**: http://localhost:8000/api/v1/docs
- **Database Admin**: http://localhost:8080
- **MinIO Console**: http://localhost:9001

## 📚 Explore Interactive Documentation

Visit http://localhost:8000/api/v1/docs to explore:

- **All API endpoints** with interactive testing
- **Request/response schemas** with examples
- **Authentication methods** with token management
- **WebSocket endpoints** for real-time data

## 🎯 Next Steps

Now that you have TradingBot running:

1. **[Learn the API](../user-guide/api-usage.md)** - Explore all endpoints
2. **[Study Strategies](../user-guide/strategies.md)** - Understand trading strategies
3. **[Configure Production](../deployment/production.md)** - Deploy to production
4. **[Develop Custom Strategies](../development/contributing.md)** - Build your own

## 🛟 Need Help?

- **Documentation**: Continue reading this documentation
- **Examples**: Check the `examples/` directory in the repository
- **Issues**: [GitHub Issues](https://github.com/tawounfouet/tradingbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tawounfouet/tradingbot/discussions)

## 🎉 Congratulations!

You now have TradingBot running successfully. You can:

- ✅ Make API requests
- ✅ Deploy trading strategies
- ✅ Run backtests
- ✅ Monitor performance
- ✅ Access interactive documentation

Start exploring the features and building your automated trading system!
