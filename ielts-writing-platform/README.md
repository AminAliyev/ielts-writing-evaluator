# IELTS Writing Evaluation Platform - V1

Production-ready AI-powered IELTS Writing preparation platform with asynchronous evaluation pipeline.

## Features

- IELTS Task 1 & Task 2 writing practice
- User authentication (signup/login/logout)
- Random task assignment
- Auto-save drafts
- Asynchronous AI-powered evaluation
- Detailed band scores and feedback
- Priority fixes and improved essays
- Submission history
- Retry failed evaluations

## Tech Stack

- Python 3.12
- Django 5+
- PostgreSQL
- HTMX + Tailwind CSS
- Pydantic v2
- Gunicorn (production)

## Windows Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 14+

### Installation

1. **Clone the repository**
```cmd
git clone <repository-url>
cd ielts-writing-platform
```

2. **Create virtual environment**
```cmd


.venv\Scripts\activate
```

3. **Install dependencies**
```cmd
pip install -r requirements.txt
```

4. **Create PostgreSQL database**
```cmd
psql -U postgres
CREATE DATABASE ielts_writing;
\q
```

5. **Configure environment**
```cmd
copy .env.example .env
```

Edit `.env` and update:
- `DATABASE_URL` with your PostgreSQL credentials
- `SECRET_KEY` (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `AI_API_KEY` with your Gemini API key (optional for testing)

6. **Run migrations**
```cmd
python manage.py migrate
```

7. **Seed initial tasks**
```cmd
python manage.py seed_tasks
```

8. **Create superuser (optional)**
```cmd
python manage.py createsuperuser
```

### Running Locally

**Terminal 1 - Django Server:**
```cmd
.venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 - Background Worker:**
```cmd
.venv\Scripts\activate
python manage.py worker
```

Access the application at: http://localhost:8000

Admin panel: http://localhost:8000/admin

### Testing Without API Key

The platform includes a mock AI provider that works without an API key for testing:
- Leave `AI_API_KEY` empty in `.env`
- Submit essays and get deterministic mock evaluations
- Perfect for development and testing

## Production Deployment

### Gunicorn

```bash
gunicorn config.wsgi:application -c gunicorn.conf.py
```

### Environment Variables (Production)

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
DATABASE_URL=postgresql://user:pass@host:5432/dbname
AI_API_KEY=your-production-api-key
```

### Worker Service

Create a systemd service or Windows service to run:
```bash
python manage.py worker
```

The worker should:
- Auto-restart on failure
- Run as a daemon/service
- Log to appropriate locations

### Database

- Use connection pooling (pgbouncer)
- Regular backups
- Monitoring

### Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Enable `CSRF_COOKIE_SECURE=True`
- [ ] Use HTTPS in production
- [ ] Regular security updates
- [ ] Implement rate limiting at reverse proxy level

## License

Proprietary - All rights reserved
