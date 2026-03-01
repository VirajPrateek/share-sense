# ShareSense Backend API

Backend API for the ShareSense expense tracking application.

**Repository:** https://github.com/VirajPrateek/share-sense.git

## Features

- JWT-based authentication
- User registration and login
- Secure password hashing with bcrypt
- PostgreSQL database integration

## Prerequisites

- Node.js (v18 or higher)
- PostgreSQL (v14 or higher)
- npm or yarn

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a PostgreSQL database:
```bash
createdb sharesense
```

3. Run the database schema:
```bash
psql -d sharesense -f database/schema.sql
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:
   - Set your database credentials
   - Set a secure JWT_SECRET (use a random string)

## Running the Application

Development mode (with auto-reload):
```bash
npm run dev
```

Production mode:
```bash
npm start
```

The server will start on `http://localhost:3000` (or the PORT specified in .env).

## API Endpoints

### Authentication

#### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response includes JWT token:
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "jwt_token_here"
}
```

#### Get Current User
```
GET /api/auth/me
Authorization: Bearer <token>
```

#### Logout
```
POST /api/auth/logout
Authorization: Bearer <token>
```

### Health Check
```
GET /health
```

## Authentication

Protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Project Structure

```
.
├── src/
│   ├── config/
│   │   └── database.js       # Database connection
│   ├── controllers/
│   │   └── authController.js # Authentication controller
│   ├── middleware/
│   │   └── auth.js           # Authentication middleware
│   ├── routes/
│   │   └── authRoutes.js     # Authentication routes
│   ├── services/
│   │   └── authService.js    # Authentication business logic
│   ├── app.js                # Express app setup
│   └── server.js             # Server entry point
├── database/
│   └── schema.sql            # Database schema
├── .env.example              # Environment variables template
├── .gitignore
├── package.json
└── README.md
```

## Error Handling

The API returns consistent error responses:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request (validation error)
- 401: Unauthorized (authentication failed)
- 404: Not Found
- 409: Conflict (e.g., email already exists)
- 500: Internal Server Error

## Security

- Passwords are hashed using bcrypt with 10 salt rounds
- JWT tokens expire after 7 days (configurable)
- CORS enabled for cross-origin requests
- Input validation on all endpoints
