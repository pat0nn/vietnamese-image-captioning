# Vietnamese Image Captioning Backend API

## 📋 Overview

This is the backend API server for the Vietnamese Image Captioning system. It provides RESTful APIs for image processing, user management, AI model inference, and administrative functions. The backend is built using Flask and integrates with Google Cloud services for scalable deployment.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config/
│   │   └── settings.py       # Application configuration
│   ├── models/
│   │   └── user.py           # Data models
│   ├── routes/               # API endpoints
│   │   ├── auth_routes.py    # Authentication APIs
│   │   ├── admin_routes.py   # Admin management APIs
│   │   ├── image_routes.py   # Image processing APIs
│   │   ├── avatar_routes.py  # User avatar APIs
│   │   ├── tts_routes.py     # Text-to-Speech APIs
│   │   └── frontend_routes.py # Frontend serving
│   ├── services/
│   │   └── model_service.py  # AI model integration
│   └── utils/
│       └── db.py            # Database utilities
├── instance/                # Instance-specific files
├── uploads/                 # Local file storage
├── requirements.txt         # Python dependencies
├── run.py                  # Application entry point
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Development setup
└── README.md              # This file
```

## 🚀 Technologies Used

### Core Framework
- **Flask 2.2.3** - Lightweight web framework
- **Flask-CORS 3.0.10** - Cross-origin resource sharing
- **Gunicorn 20.1.0** - WSGI HTTP Server for production

### AI & Machine Learning
- **PyTorch 2.0+** - Deep learning framework
- **Transformers 4.27.3+** - Hugging Face model library
- **SentencePiece 0.1.97+** - Text tokenization
- **Pillow 9.4.0+** - Image processing

### Database & Storage
- **PostgreSQL** - Primary database
- **psycopg2-binary 2.9.5+** - PostgreSQL adapter
- **Google Cloud Storage** - Cloud file storage

### Authentication & Security
- **PyJWT 2.6.0+** - JSON Web Token implementation
- **bcrypt 4.0.1+** - Password hashing

### Cloud Services
- **Google Cloud Text-to-Speech** - Audio generation
- **Google Cloud Secret Manager** - Secrets management
- **Google Cloud Storage** - File storage

## ✨ Key Features

### 🔐 Authentication System
- JWT-based authentication with 30-day token expiration
- User registration and login
- Role-based access control (Admin/User)
- Secure password hashing with bcrypt

### 🖼️ Image Processing
- Multi-format image upload support
- AI-powered Vietnamese caption generation
- Batch processing capabilities
- Image metadata extraction and storage

### 👥 User Management
- User profile management
- Avatar upload and management
- Activity tracking and analytics
- Admin dashboard for user oversight

### ⭐ Rating & Contribution System
- User rating system for caption quality (1-5 stars)
- Community contribution management
- Admin review and approval workflow
- Statistics and analytics tracking

### 📊 Analytics & Monitoring
- Daily usage statistics
- Performance metrics tracking
- User activity monitoring
- Admin dashboard with comprehensive analytics

### 🎙️ Text-to-Speech Integration
- Vietnamese text-to-speech conversion
- Google Cloud TTS integration
- Audio file generation and storage

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Google Cloud credentials (for production features)
- Docker & Docker Compose (optional)

### Local Development Setup

#### 1. Clone and Setup Environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### 2. Database Configuration
Create a PostgreSQL database and update environment variables:

```bash
# Create .env file
echo "DB_HOST=localhost" > .env
echo "DB_PORT=5432" >> .env
echo "DB_NAME=image_caption_db" >> .env
echo "DB_USER=your_username" >> .env
echo "DB_PASSWORD=your_password" >> .env
```

#### 3. Google Cloud Setup (Optional)
For full functionality, set up Google Cloud credentials:
```bash
# Place your service account key
cp path/to/your/service-account.json your_key.json

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=your_key.json
```

#### 4. Initialize Database
```bash
python run.py
```
The application will automatically initialize the database schema on first run.

### Docker Setup

#### Development with Docker Compose
```bash
docker-compose up --build
```

#### Production Docker Build
```bash
docker build -t vietnamese-image-captioning-backend .
docker run -p 5000:5000 vietnamese-image-captioning-backend
```

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/register` | User registration | ❌ |
| `POST` | `/api/auth/login` | User login | ❌ |
| `POST` | `/api/auth/logout` | User logout | ✅ |
| `GET` | `/api/user` | Get current user info | ✅ |

### Image Processing
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/caption` | Generate image caption | ❌ |
| `GET` | `/api/images` | Get image list | ✅ |
| `GET` | `/api/image/<id>` | Get specific image | ✅ |
| `DELETE` | `/api/image/<id>` | Delete image | ✅ |

### Rating & Contribution
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/rate/<image_id>` | Rate caption quality | ❌ |
| `GET` | `/api/ratings/<image_id>` | Get image ratings | ❌ |
| `POST` | `/api/contribute` | Submit contribution | ✅ |
| `GET` | `/api/contributions` | Get all contributions | ✅ |
| `GET` | `/api/user/contributions` | Get user contributions | ✅ |

### Admin Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/check` | Check admin status | ✅ Admin |
| `GET` | `/api/admin/users` | List all users | ✅ Admin |
| `POST` | `/api/admin/users` | Create new user | ✅ Admin |
| `PUT` | `/api/admin/users/<id>` | Update user | ✅ Admin |
| `DELETE` | `/api/admin/users/<id>` | Delete user | ✅ Admin |
| `GET` | `/api/admin/contributions/pending` | Get pending contributions | ✅ Admin |
| `PUT` | `/api/admin/contributions/<id>` | Review contribution | ✅ Admin |
| `GET` | `/api/admin/stats` | Get system statistics | ✅ Admin |

### Utility APIs
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/tts` | Text-to-speech conversion | ❌ |
| `POST` | `/api/upload-avatar` | Upload user avatar | ✅ |
| `GET` | `/api/avatar/<filename>` | Get avatar image | ❌ |

## 🗄️ Database Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    biography TEXT,
    position VARCHAR(100),
    country VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'active',
    avatar VARCHAR(255) DEFAULT 'default.jpg',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### images
```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(255) UNIQUE NOT NULL,
    image_path VARCHAR(500),
    user_caption TEXT,
    ai_caption TEXT,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### caption_ratings
```sql
CREATE TABLE caption_ratings (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(255) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### contributions
```sql
CREATE TABLE contributions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    image_id VARCHAR(255) NOT NULL,
    caption TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    reviewer_id INTEGER REFERENCES users(id),
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=image_caption_db
DB_USER=postgres
DB_PASSWORD=your_password

# Application Configuration
PORT=5000
MODEL_PATH=/path/to/model/artifacts

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account.json
GCS_BUCKET_NAME=vic-storage

# Security
SECRET_KEY=your-secret-key-here
```

### CORS Configuration
The API supports the following origins:
- `http://localhost:3000` (React development)
- `http://localhost:5173` (Vite development)
- `https://vic.phambatrong.com` (Production)
- `https://vietnamese-image-captioning.web.app` (Firebase)

## 🚀 Deployment

### Local Development
```bash
python run.py
```
Server runs on `http://localhost:5000`

### Production Deployment
```bash
gunicorn -b 0.0.0.0:$PORT -w 4 --threads 2 --timeout 0 run:app
```

### Google Cloud Run
The application is configured for Google Cloud Run deployment with:
- Multi-worker Gunicorn setup
- Google Cloud Storage integration
- Cloud SQL PostgreSQL support
- Secret Manager integration


## 📊 Performance & Monitoring

### Metrics Tracked
- Daily active users
- API response times
- Image processing statistics
- Model inference performance
- Error rates and logging

### Logging
The application uses Python's logging module with INFO level by default. Logs include:
- Request/response details
- Model loading status
- Database operations
- Error tracking

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt rounds
- **CORS Protection**: Configured for specific origins only
- **Input Validation**: Request validation and sanitization
- **Rate Limiting**: Built-in request throttling
- **SQL Injection Protection**: Parameterized queries


