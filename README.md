# Supabase Auth API

A production-ready authentication API scaffolding template using FastAPI and Supabase.

## Features

- 🔐 **Email/Password Authentication** - Complete signup, login, logout, password reset
- 🌟 **Google OAuth** - Social login with Google authentication
- 🛡️ **JWT Token Validation** - Production-level security with proper token verification
- 🌐 **Supabase Integration** - Direct integration with Supabase Auth
- 🔑 **Google Secret Manager** - Production secret management support
- ⚡ **FastAPI** - Modern, fast Python web framework
- 📝 **Auto Documentation** - Interactive API docs at `/docs`

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# Supabase Configuration (Required)
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_JWT_SECRET=your_supabase_jwt_secret_here

# Google Cloud Configuration (Optional - for production)
USE_GSM=false
GCP_PROJECT_ID=your_gcp_project_id

# Application Configuration (Optional)
DEBUG=false
TESTING=false
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
```

### 3. Run the API

```bash
# Development server
uvicorn src.api.api:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn src.api.api:app --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication

- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/reset-password` - Request password reset
- `GET /api/v1/auth/session-check` - Validate session

### Google OAuth

- `POST /api/v1/auth/oauth/login` - Initiate Google OAuth login
- `POST /api/v1/auth/oauth/callback` - Handle Google OAuth callback

### System

- `GET /health` - Health check endpoint

## Getting Supabase Credentials

1. Create a project at [supabase.com](https://supabase.com)
2. Go to Project Settings → API
3. Copy the following values to your `.env` file:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY`
   - **JWT Secret** → `SUPABASE_JWT_SECRET`

## Setting Up Google OAuth

1. **Google Cloud Console Setup**:

   - Create a project in [Google Cloud Console](https://console.cloud.google.com)
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URI: `https://your-project-ref.supabase.co/auth/v1/callback`
   - Add authorized JavaScript origin: `https://your-project-ref.supabase.co`

2. **Supabase Dashboard Setup**:
   - Go to Authentication → Providers in your Supabase dashboard
   - Enable Google provider
   - Add your Google OAuth Client ID and Client Secret

**Note**: Supabase manages the Google OAuth flow completely. You don't need Google OAuth credentials in your FastAPI environment variables.

## Development

The codebase is structured for easy extension:

```
src/
├── api/
│   ├── endpoints/     # API route definitions
│   ├── utils/         # Shared utilities
│   └── dependencies.py
├── core/              # Core configuration
├── models/            # Pydantic models
└── services/          # Business logic
```

## Production Deployment

For production, set `USE_GSM=true` and configure Google Secret Manager with your Supabase credentials.

## License

MIT License
