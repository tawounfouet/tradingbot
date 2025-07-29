


# 🚀 TradingBot - Advanced Cryptocurrency Trading Bot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI](https://github.com/tawounfouet/tradingbot/workflows/CI/badge.svg)](https://github.com/tawounfouet/tradingbot/actions/workflows/ci.yml)
[![Documentation](https://github.com/tawounfouet/tradingbot/workflows/Deploy%20Documentation/badge.svg)](https://github.com/tawounfouet/tradingbot/actions/workflows/docs.yml)
[![Documentation Site](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://tawounfouet.github.io/tradingbot/)

> **Advanced cryptocurrency trading bot with automated strategies built with FastAPI, featuring real-time market data integration, multiple database support, and comprehensive backtesting capabilities.**

## 📚 Documentation

Visit our comprehensive documentation at: **[https://tawounfouet.github.io/tradingbot/](https://tawounfouet.github.io/tradingbot/)**

- 📖 [Getting Started Guide](https://tawounfouet.github.io/tradingbot/getting-started/installation/)
- 🔧 [Configuration Guide](https://tawounfouet.github.io/tradingbot/getting-started/configuration/)
- 🐳 [Docker Setup](https://tawounfouet.github.io/tradingbot/getting-started/docker/)
- 📊 [API Reference](https://tawounfouet.github.io/tradingbot/api/overview/)
- 🧠 [Strategy Development](https://tawounfouet.github.io/tradingbot/user-guide/strategies/)

## ✨ Features

- 🤖 **Automated Trading Strategies** - Multiple built-in strategies with customizable parameters
- 📊 **Real-time Market Data** - Integration with Binance and other exchanges
- 🔐 **Secure Authentication** - JWT-based user authentication and authorization
- 📈 **Technical Analysis** - Advanced indicators (RSI, Bollinger Bands, Moving Averages)
- 🐳 **Docker Ready** - Containerized for easy deployment
- 🧪 **Comprehensive Testing** - Unit and integration tests with pytest
- 📝 **API Documentation** - Auto-generated OpenAPI/Swagger docs
- 🔄 **Background Tasks** - Async task processing for strategy execution

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/tawounfouet/tradingbot.git
cd tradingbot

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install with development dependencies
pip install -e ".[dev,test]"

# Start the development server
make run
```

Visit `http://localhost:8000/api/v1/docs` for the interactive API documentation.

## 📁 Project Structure

```
tradingbot/
├── src/tradingbot/          # Main application package
│   ├── config/              # Configuration management
│   ├── models/              # Database models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   ├── strategies/          # Trading strategies
│   └── schemas/             # Pydantic schemas
├── pyproject.toml           # Modern Python project configuration
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-service setup
└── Makefile                 # Development commands
```

## 🛠️ Development Commands

```bash
make help          # Show all available commands
make run           # Start development server
make test          # Run tests
make format        # Format code with black & isort
make lint          # Run linting checks
make docker-up     # Start with Docker
make clean         # Clean build artifacts
```

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Or use the Makefile
make docker-up
```

## 📊 Trading Strategies

Available strategies:
- **Moving Average Crossover** - Classic trend-following strategy
- **RSI Reversal** - Mean reversion based on RSI indicator
- **Bollinger Bands** - Volatility-based trading signals
- **Multi-Indicator** - Combined technical analysis approach

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
# API Configuration
SECRET_KEY=your-secret-key
API_PREFIX=/api/v1
DEBUG=true

# Database
DATABASE_URL=postgresql://user:pass@localhost/tradingbot

# Binance API (for live trading)
BINANCE_API_KEY=your-api-key
BINANCE_SECRET_KEY=your-secret-key
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/test_strategies.py -v
```

## 📚 Documentation

- [Complete Setup Guide](README_COMPLETE.md) - Detailed installation and configuration
- [API Documentation](http://localhost:8000/api/v1/docs) - Interactive Swagger docs
- [Strategy Development](src/tradingbot/docs/strategies-guide/) - Custom strategy creation
- [Architecture](src/tradingbot/docs/ARCHITECTURE_REFACTORING_SUCCESS.md) - System design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test && make lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational purposes only. Cryptocurrency trading involves significant risk of loss. Always do your own research and never trade with money you cannot afford to lose.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices.**
```sh
crypto-bot-team/
├── src/
│   └── backend/
│       ├── config/                    # Configuration centralisée
│       │   ├── __init__.py
│       │   ├── settings.py           # Pydantic settings (comme Django settings)
│       │   ├── database.py           # Configuration DB
│       │   ├── security.py           # JWT, hashing, etc.
│       │   └── constants.py          # Constantes globales
│       │
│       ├── models/                   # Modèles SQLAlchemy (comme Django models)
│       │   ├── __init__.py
│       │   ├── base.py              # BaseModel avec mixins
│       │   ├── user.py              # User, UserSession, UserSettings
│       │   ├── strategy.py          # Strategy, StrategyDeployment
│       │   ├── trading.py           # Order, Transaction, Position
│       │   ├── market.py            # MarketData, Symbol
│       │   └── backtest.py          # BacktestResult
│       │
│       ├── schemas/                  # Pydantic schemas (comme DRF serializers)
│       │   ├── __init__.py
│       │   ├── user.py              # UserCreate, UserResponse, etc.
│       │   ├── strategy.py          # StrategyCreate, StrategyResponse
│       │   ├── trading.py           # OrderCreate, OrderResponse
│       │   ├── market.py            # MarketDataResponse
│       │   └── common.py            # Schemas communs (pagination, etc.)
│       │
│       ├── services/                 # Logique métier (comme Django services)
│       │   ├── __init__.py
│       │   ├── auth_service.py      # Authentification, JWT
│       │   ├── user_service.py      # CRUD users, logique métier
│       │   ├── strategy_service.py  # Gestion stratégies
│       │   ├── trading_service.py   # Logique trading
│       │   ├── market_service.py    # Données de marché
│       │   ├── backtest_service.py  # Backtesting
│       │   ├── external/            # Services externes
│       │   │   ├── __init__.py
│       │   │   ├── binance_service.py
│       │   │   ├── minio_service.py
│       │   │   └── redis_service.py
│       │   └── notifications/       # Services de notification
│       │       ├── __init__.py
│       │       ├── email_service.py
│       │       └── websocket_service.py
│       │
│       ├── controllers/              # Contrôleurs (logique API)
│       │   ├── __init__.py
│       │   ├── auth_controller.py   # Login, register, refresh
│       │   ├── user_controller.py   # CRUD users
│       │   ├── strategy_controller.py
│       │   ├── trading_controller.py
│       │   ├── market_controller.py
│       │   └── backtest_controller.py
│       │
│       ├── routes/                   # Routes FastAPI (comme Django URLs)
│       │   ├── __init__.py
│       │   ├── auth.py              # Routes authentification
│       │   ├── users.py             # Routes users
│       │   ├── strategies.py        # Routes stratégies
│       │   ├── trading.py           # Routes trading
│       │   ├── market_data.py       # Routes market data
│       │   ├── backtest.py          # Routes backtesting
│       │   └── websockets.py        # WebSocket routes
│       │
│       ├── middleware/               # Middlewares FastAPI
│       │   ├── __init__.py
│       │   ├── cors.py
│       │   ├── auth.py              # Middleware auth
│       │   ├── rate_limit.py
│       │   └── logging.py
│       │
│       ├── utils/                    # Utilitaires
│       │   ├── __init__.py
│       │   ├── dependencies.py      # FastAPI dependencies
│       │   ├── validators.py        # Validateurs custom
│       │   ├── decorators.py        # Décorateurs custom
│       │   ├── exceptions.py        # Exceptions custom
│       │   ├── pagination.py        # Pagination helpers
│       │   └── helpers.py           # Fonctions utilitaires
│       │
│       ├── strategies/               # Moteur de stratégies
│       │   ├── __init__.py
│       │   ├── base.py              # Classe de base Strategy
│       │   ├── registry.py          # Registre des stratégies
│       │   ├── indicators/          # Indicateurs techniques
│       │   │   ├── __init__.py
│       │   │   ├── moving_average.py
│       │   │   ├── rsi.py
│       │   │   └── bollinger_bands.py
│       │   └── implementations/     # Stratégies concrètes
│       │       ├── __init__.py
│       │       ├── ma_crossover.py
│       │       ├── rsi_reversal.py
│       │       └── grid_trading.py
│       │
│       ├── database/                 # Gestion base de données
│       │   ├── __init__.py
│       │   ├── connection.py        # Connexions DB
│       │   ├── migrations/          # Migrations Alembic
│       │   │   ├── versions/
│       │   │   ├── alembic.ini
│       │   │   ├── env.py
│       │   │   └── script.py.mako
│       │   └── seeds/               # Données de test
│       │       ├── __init__.py
│       │       ├── users.py
│       │       └── strategies.py
│       │
│       ├── monitoring/               # Monitoring et logs
│       │   ├── __init__.py
│       │   ├── logging.py           # Configuration logs
│       │   ├── metrics.py           # Métriques
│       │   └── health.py            # Health checks
│       │
│       ├── main.py                  # Point d'entrée FastAPI
│       └── wsgi.py                  # Pour déploiement WSGI
│
├── tests/                           # Tests
│   ├── __init__.py
│   ├── conftest.py                 # Configuration pytest
│   ├── unit/                       # Tests unitaires
│   │   ├── test_models/
│   │   ├── test_services/
│   │   ├── test_controllers/
│   │   └── test_utils/
│   ├── integration/                # Tests d'intégration
│   │   ├── test_api/
│   │   ├── test_database/
│   │   └── test_external/
│   └── fixtures/                   # Fixtures de test
│       ├── users.json
│       └── strategies.json
│
├── scripts/                        # Scripts utilitaires
│   ├── setup_db.sh
│   ├── migrate.py
│   ├── seed_data.py
│   └── start_dev.py
│
├── docker/                         # Configuration Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
│
├── docs/                           # Documentation
│   ├── api/
│   ├── models/
│   └── deployment/
│
├── .env.example
├── .gitignore
├── pyproject.toml                  # Poetry
├── requirements.txt                # Pip fallback
├── Makefile
└── README.md
```

```sh
# Avant chaque commit
python scripts/validate_code.py

# En cas de problème
python scripts/debug_registration.py

# Test global du système  
python scripts/test_auth_system.py


pip install -r requirements.txt

source .venv/bin/activate && cd src/tradingbot && python main.py
```


 :

