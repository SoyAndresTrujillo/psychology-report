# Psychologist Appointment Management System

A Django-based system for managing patient registration, psychologist profiles, doctor's office management, and appointment scheduling.

## 📋 Features

- **Account Management**: Register patients and psychologists
- **Office Management**: Manage doctor's offices with contact information
- **Doctor Profiles**: Link psychologists to offices with specialties
- **Appointment Scheduling**: Schedule appointments between patients and psychologists
- **Reporting**: Comprehensive appointment reports

## 🛠️ Tech Stack

- **Backend**: Django 5.1
- **Database**: PostgreSQL 15
- **Container**: Docker & Docker Compose
- **Python**: 3.11

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Setup

1. **Clone the repository**
   ```bash
   cd /path/to/project
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start the application**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Create superuser (optional)**
   ```bash
   docker exec -it psychologist_web python manage.py createsuperuser
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

### Stop the application
```bash
docker-compose -f docker-compose.dev.yml down
```

### If we need to install a new package
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```
and after re run again

## 📁 Project Structure

```
psychologist_system/          # Django project configuration
├── settings.py              # Project settings
├── urls.py                  # Main URL configuration
└── wsgi.py                  # WSGI configuration

accounts/                    # User account management
├── models.py               # Account model
├── forms.py                # Account forms
├── views.py                # Account views
└── urls.py                 # Account URLs

offices/                     # Doctor's office management
├── models.py               # DoctorsOffice model
├── forms.py                # Office forms
├── views.py                # Office views
└── urls.py                 # Office URLs

doctors/                     # Doctor profile management
├── models.py               # Doctor model
├── forms.py                # Doctor forms
├── views.py                # Doctor views
└── urls.py                 # Doctor URLs

appointments/                # Appointment scheduling
├── models.py               # Appointment model
├── forms.py                # Appointment forms
├── views.py                # Appointment views
└── urls.py                 # Appointment URLs

api/                        # REST API endpoints
├── views.py               # API views
└── urls.py                # API URLs

templates/                  # HTML templates
├── base.html
├── 404.html
├── accounts/
├── appointments/
├── doctors/
└── offices/

static/                     # Static files (CSS, JS)
└── css/
    └── styles.css
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/create` | Create new account |
| POST | `/api/appointments/create` | Create new appointment |
| POST | `/api/doctors/create` | Create doctor profile |
| POST | `/api/doctors_office/create` | Create doctor's office |
| GET | `/api/appointment-report` | Get appointment report |

## 📝 Development

### Running Migrations
```bash
docker exec -it psychologist_web python manage.py makemigrations
docker exec -it psychologist_web python manage.py migrate
```

### Access Django Shell
```bash
docker exec -it psychologist_web python manage.py shell
```

### View Logs
```bash
docker logs -f psychologist_web
```

## 🎓 Educational Content

This project demonstrates key Django concepts from the official tutorials:

- ✅ **Tutorial 1**: Project setup, apps, and configuration
- ✅ **Tutorial 2**: Models, migrations, and admin interface
- ✅ **Tutorial 3**: Views, URLs, and templates
- ✅ **Tutorial 4**: Forms and data processing

## 📄 License

Educational project for university coursework.

## 👥 Authors

- Andres Trujillo
