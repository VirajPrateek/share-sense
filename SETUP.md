# Sharesense Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Setup Database

Create a PostgreSQL database:
```bash
createdb sharesense
```

Run the schema:
```bash
psql -d sharesense -f database/schema.sql
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and set your values:
- `DB_PASSWORD`: Your PostgreSQL password
- `JWT_SECRET`: A random secret string (e.g., generate with `openssl rand -base64 32`)

### 4. Start the Server

Development mode:
```bash
npm run dev
```

Production mode:
```bash
npm start
```

### 5. Test the API

Check if the server is running:
```bash
curl http://localhost:3000/health
```

Register a user:
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

Login:
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

The login response will include a JWT token. Use it for authenticated requests:
```bash
curl http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Running Tests

Run all tests:
```bash
npm test
```

Run tests in watch mode:
```bash
npm run test:watch
```

## Troubleshooting

### Database Connection Issues

If you see "database connection failed":
1. Check PostgreSQL is running: `pg_isready`
2. Verify credentials in `.env`
3. Ensure database exists: `psql -l | grep sharesense`

### Port Already in Use

If port 3000 is already in use, change the `PORT` in `.env`:
```
PORT=3001
```

### JWT Token Issues

If you see "Invalid or expired token":
1. Ensure `JWT_SECRET` is set in `.env`
2. Check token is included in Authorization header
3. Verify token format: `Bearer <token>`
