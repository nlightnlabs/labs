# SaaS Application Template

A comprehensive, production-ready SaaS application template with a React frontend and FastAPI backend.

## Features

- **Authentication**: Email/password login, registration, password reset, SAML SSO support
- **User Management**: Profile management, session handling, role-based access control
- **Theming**: Light/dark mode with customizable CSS properties
- **Internationalization**: Multi-language support (English, Spanish, French, German, Japanese)
- **Settings**: User preferences, organization management, notification settings
- **API**: RESTful API with comprehensive endpoints
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Storage**: AWS S3 and Azure Blob Storage support
- **Docker**: Full containerization with Docker Compose

## Tech Stack

### Frontend
- React 18+ with TypeScript
- Redux Toolkit with Redux Persist
- Tailwind CSS
- React Router
- i18next
- Axios

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy ORM
- Pydantic
- JWT Authentication
- SAML 2.0 SSO

### Infrastructure
- Docker & Docker Compose
- PostgreSQL
- Redis (optional)
- AWS S3 / Azure Blob Storage

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (or use Docker)

### Using Docker (Recommended)

1. Clone and configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Project Structure

```
/template
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   │   ├── common/      # Button, Input, Card, etc.
│   │   │   └── layout/      # Header, Sidebar, Layout
│   │   ├── features/        # Feature modules
│   │   │   ├── auth/        # Authentication
│   │   │   ├── dashboard/   # Dashboard page
│   │   │   └── settings/    # Settings page
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API clients
│   │   ├── store/           # Redux store
│   │   ├── styles/          # CSS and theming
│   │   ├── i18n/            # Translations
│   │   └── types/           # TypeScript types
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Config and security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities
│   │   └── main.py          # App entry point
│   ├── tests/               # Test files
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete account
- `PATCH /api/v1/users/me/password` - Change password
- `GET /api/v1/users/me/sessions` - Get active sessions

### Settings
- `GET /api/v1/settings/preferences` - Get preferences
- `PUT /api/v1/settings/preferences` - Update preferences
- `GET /api/v1/settings/organization` - Get organization (admin)
- `PUT /api/v1/settings/organization` - Update organization (admin)

### Notifications
- `GET /api/v1/notifications` - List notifications
- `PATCH /api/v1/notifications/{id}/read` - Mark as read
- `DELETE /api/v1/notifications/{id}` - Delete notification

## Environment Variables

See `.env.example` for all available configuration options.

## Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Testing

### Backend
```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

### Frontend
```bash
cd frontend
npm test
npm run test:coverage  # With coverage
```

## Deployment

### Production Build

Frontend:
```bash
cd frontend
npm run build
```

Backend:
```bash
# No build required, just ensure dependencies are installed
pip install -r requirements.txt
```

### Docker Production

```bash
docker-compose -f docker-compose.yml up -d --build
```

## Security Features

- JWT authentication with refresh tokens
- Password hashing with bcrypt (cost factor 12)
- Rate limiting on authentication endpoints
- Account lockout after failed attempts
- CORS configuration
- Security headers (XSS, CSRF, Content-Type)
- Input validation and sanitization
- SQL injection prevention

## Future Module Integration

Future modules should:
1. Register their Redux slice with the global store
2. Add navigation items via configuration
3. Use global theme variables for consistent styling
4. Respect global language settings
5. Access user context from global state
6. Follow established API patterns
7. Use provided database and storage utilities

## License

MIT License
