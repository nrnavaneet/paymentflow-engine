# API Documentation

## Authentication

All API endpoints (except `/api/auth/*`) require authentication via JWT token.

Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token

### Accounts
- `POST /api/accounts` - Create account
- `GET /api/accounts` - List user accounts
- `GET /api/accounts/<id>/balance` - Get account balance

### Transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions` - List transactions
- `GET /api/transactions/<id>` - Get transaction details

### Payments
- `POST /api/payments` - Process payment
- `GET /api/payments` - List payments

### Settlements (Admin)
- `POST /api/settlements/batches` - Create settlement batch
- `POST /api/settlements/batches/<id>/process` - Process settlement batch

### Compliance
- `POST /api/compliance/kyc` - Submit KYC documents
- `GET /api/compliance/kyc/status` - Get KYC status

## TODO: Complete API documentation with request/response examples
## TODO: Add error code documentation
## TODO: Add rate limiting documentation


