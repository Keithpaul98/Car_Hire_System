# 🚀 Getting Started Guide

## Quick Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Git

### 1. Project Structure Setup
```bash
mkdir backend frontend docs
```

### 2. Backend Setup (Django)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install django djangorestframework
django-admin startproject config .
python manage.py startapp authentication
python manage.py startapp vehicles
python manage.py startapp bookings
```

### 3. Frontend Setup (Next.js)
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app
npm install @tanstack/react-query axios
```

### 4. Database Setup
```bash
createdb car_hire_system
python manage.py migrate
python manage.py createsuperuser
```

### 5. Environment Variables
Create `.env` files for configuration:

**Backend (.env)**
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/car_hire_system
REDIS_URL=redis://localhost:6379
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 6. Run Development Servers
```bash
# Backend
cd backend && python manage.py runserver

# Frontend
cd frontend && npm run dev
```

## Next Steps
1. Follow DEVELOPMENT_WORKFLOW.md for detailed development process
2. Review ARCHITECTURE.md for system design
3. Start with Phase 1 implementation

The project is now ready for enterprise-grade development with proper documentation, architecture, and workflow guidelines in place.
