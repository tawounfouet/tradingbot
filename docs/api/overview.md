# API Overview

The TradingBot API is built with FastAPI and provides a comprehensive RESTful interface for all trading operations.

## 🌐 Base Information

- **Base URL**: `http://localhost:8000/api/v1`
- **Protocol**: HTTP/HTTPS
- **Format**: JSON
- **Authentication**: JWT Bearer Token
- **Documentation**: Available at `/docs` and `/redoc`

## 🔐 Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

```bash
curl -X POST "/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
```

## 📚 API Sections

### Authentication & Users
- **`/auth/*`** - Authentication endpoints
- **`/users/*`** - User management

### Trading Operations
- **`/strategies/*`** - Strategy management
- **`/trading/*`** - Trading operations
- **`/backtest/*`** - Backtesting

### Market Data
- **`/market/*`** - Market data endpoints
- **`/websocket/*`** - Real-time data streams

### System
- **`/health`** - Health checks
- **`/metrics`** - System metrics

## 🚀 Quick Examples

### Health Check
```bash
curl "http://localhost:8000/health"
```

### Get All Strategies
```bash
curl "http://localhost:8000/api/v1/strategies"
```

### Deploy a Strategy
```bash
curl -X POST "http://localhost:8000/api/v1/strategies/deploy" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"strategy_id": "moving_average_crossover", "symbol": "BTCUSDT"}'
```

## 📖 Interactive Documentation

Visit these URLs when the server is running:

- **Swagger UI**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **ReDoc**: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
- **OpenAPI JSON**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

## 🔄 Response Format

All API responses follow this structure:

### Success Response
```json
{
  "data": { /* response data */ },
  "message": "Success",
  "timestamp": "2025-07-29T12:00:00Z"
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { /* error details */ }
  },
  "timestamp": "2025-07-29T12:00:00Z"
}
```

## 📊 Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request validation failed |
| 500 | Server Error | Internal server error |

## 🔌 WebSocket Support

Real-time data is available via WebSocket connections:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/market-data');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Market data:', data);
};
```

## 📝 Request/Response Examples

For detailed examples of each endpoint, see the specific API documentation pages:

- [Authentication API](authentication.md)
- [Users API](users.md)
- [Strategies API](strategies.md)
- [Trading API](trading.md)
- [Market Data API](market-data.md)
