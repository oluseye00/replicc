# RepliC - AI Content Creation Platform

RepliC is an intelligent content creation platform that leverages AI for writing and video matching to help creators produce engaging content for all social media platforms.

## 🚀 Features

- **AI-Powered Content Generation** - Create engaging posts using advanced language models
- **Intelligent Video Matching** - Automatically pair your content with relevant video clips
- **Multi-Platform Support** - Optimize content for different social media platforms
- **User Authentication** - Secure user accounts with JWT authentication
- **RESTful API** - Full API access for integrations and custom applications
- **Responsive Design** - Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

RepliC is built with a modern, scalable architecture:

- **Backend:** Django 4.2 with Django REST Framework
- **Database:** PostgreSQL (SQLite for development)
- **Cache & Queue:** Redis with Celery for background tasks
- **Frontend:** React with TypeScript (if applicable)
- **Deployment:** Docker containers with CI/CD pipeline
- **Monitoring:** Sentry for error tracking and performance monitoring

## 📋 Requirements

- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL 15+ (production)
- Redis 7+ (for caching and background tasks)
- Docker & Docker Compose (recommended for development)

## 🛠️ Development Setup

### Option 1: Docker Development (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/replic.git
cd replic

# Start all services with Docker Compose
docker-compose up -d

# Run database migrations
docker-compose exec web python manage.py migrate

# Create a superuser
docker-compose exec web python manage.py createsuperuser

# Visit http://localhost:8000
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/your-username/replic.git
cd replic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (if applicable)
cd frontend && npm install && npm run build && cd ..

# Setup environment variables
cp .env.development .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# In another terminal, start Celery worker (optional)
celery -A replic worker -l info
```

## 🧪 Testing

### Run All Tests

```bash
# Using the pipeline test script (recommended)
./test_pipeline.py

# Or run tests individually
python manage.py test
cd frontend && npm test  # If using frontend tests
```

### Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Run once to check everything
```

## 🚀 Deployment

### Environment Setup

RepliC uses three environments with automatic deployments:

1. **Development** (`develop` branch) → `dev.replic.com`
2. **QA/Staging** (`staging` branch) → `qa.replic.com`
3. **Production** (`main` branch) → `replic.com`

### Branch Strategy

```bash
# Feature development
git checkout develop
git checkout -b feature/new-feature
# ... make changes ...
git push origin feature/new-feature
# Create PR to develop

# Release process
develop → staging → main
```

See [BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md) for detailed workflow.

### Manual Deployment

```bash
# Build and deploy with Docker
docker build -t replic:latest .
docker run -p 8000:8000 replic:latest

# Or use your preferred hosting platform
# (Railway, Render, Heroku, AWS, etc.)
```

## 📊 CI/CD Pipeline

Our GitHub Actions pipeline automatically:

- ✅ Runs comprehensive tests (unit, integration, frontend)
- 🔍 Performs security scans (Bandit)
- 📏 Checks code quality (Black, isort, flake8)
- 🚀 Deploys to appropriate environment based on branch
- 📈 Reports test coverage
- 🔄 Supports automatic rollback

## 🔧 Configuration

### Environment Variables

Key environment variables for each environment:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=replic.com,www.replic.com

# API Keys
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
STRIPE_PUBLISHABLE_KEY=your-stripe-key
STRIPE_SECRET_KEY=your-stripe-secret

# File Storage (S3)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=replic-media
```

See environment-specific `.env.*` files for complete configuration.

## 📚 API Documentation

- **Development:** http://localhost:8000/api/docs/
- **QA:** https://qa.replic.com/api/docs/
- **Production:** https://replic.com/api/docs/

API documentation is automatically generated from code using DRF Spectacular.

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** and ensure tests pass (`./test_pipeline.py`)
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Create a Pull Request**

### Code Style

We use automated code formatting and linting:

- **Black** for Python code formatting
- **isort** for import sorting
- **flake8** for Python linting
- **Bandit** for security scanning
- **Prettier** for frontend formatting (if applicable)

## 🐛 Debugging

### Common Issues

**Database Connection Issues:**
```bash
# Check if PostgreSQL is running
docker-compose ps db
# View database logs
docker-compose logs db
```

**Celery Worker Issues:**
```bash
# Check worker status
docker-compose ps celery
# View worker logs
docker-compose logs celery
```

**Frontend Build Issues:**
```bash
# Clear node modules and reinstall
rm -rf frontend/node_modules
cd frontend && npm install
```

### Logs and Monitoring

- **Development:** Console logs and `replic_dev.log`
- **QA:** Structured logging + Sentry (10% sample rate)
- **Production:** Sentry monitoring (1% sample rate) + CloudWatch/similar

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework teams
- React and TypeScript communities
- All the amazing open-source libraries that make RepliC possible

## 📞 Support

- **Documentation:** [docs.replic.com](https://docs.replic.com)
- **Issues:** [GitHub Issues](https://github.com/your-username/replic/issues)
- **Email:** support@replic.com

---

Made with ❤️ and AI by the RepliC team