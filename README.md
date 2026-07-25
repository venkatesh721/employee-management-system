# Employee Management System

A full-stack Employee Management System built with React, FastAPI, and PostgreSQL. Features JWT authentication, comprehensive CRUD operations, interactive dashboard with charts, attendance tracking, department management, and a responsive, professional UI.

## Features

- **Authentication & Authorization**: JWT-based login/registration with password hashing and protected routes
- **Employee Management**: Full CRUD with search, filter, pagination, and sorting
- **Department Management**: Create and manage departments with employee counts
- **Attendance Tracking**: Check-in/check-out, daily attendance view, monthly summaries
- **Interactive Dashboard**: Statistics cards, attendance charts, department distribution, recent employees
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Admin Interface**: Comprehensive management interface with role-based access
- **CI/CD Ready**: GitHub Actions pipeline with automated testing and deployment

## Screenshots

| Dashboard | Employees | Attendance |
|-----------|-----------|------------|
| `[Dashboard Screenshot]` | `[Employees Screenshot]` | `[Attendance Screenshot]` |

## Technology Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite | Build tool and dev server |
| React Router v6 | Client-side routing |
| Axios | HTTP client for API calls |
| Recharts | Charts and data visualization |
| React Hot Toast | Notification system |
| CSS Variables | Theming and styling |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | Python web framework |
| SQLAlchemy | ORM and database abstraction |
| Pydantic | Data validation and schemas |
| Python-Jose | JWT token handling |
| Passlib | Password hashing (bcrypt) |
| Alembic | Database migrations |
| Uvicorn | ASGI server |

### Database
| Technology | Purpose |
|------------|---------|
| PostgreSQL | Primary database |
| SQLAlchemy | Database abstraction layer |

### DevOps
| Technology | Purpose |
|------------|---------|
| GitHub Actions | CI/CD pipeline |
| Vercel | Frontend deployment |
| Railway/Render | Backend deployment |

## System Architecture

```
User Browser
     |
     | HTTPS
     v
Vercel (Frontend - React SPA)
     |
     | API Calls (/api/*)
     v
Railway/Render (Backend - FastAPI)
     |
     | SQL
     v
PostgreSQL Database
```

The frontend is a single-page application (SPA) built with React. It communicates with the backend via RESTful API calls over HTTP/HTTPS. The backend is a FastAPI application that handles business logic, authentication, and database operations. PostgreSQL stores all persistent data.

## Folder Structure

```
employee-management-system/
├── backend/
│   ├── alembic/
│   │   ├── versions/          # Migration versions
│   │   └── env.py             # Alembic environment config
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── auth.py         # Authentication endpoints
│   │   │       ├── employees.py    # Employee CRUD endpoints
│   │   │       ├── departments.py  # Department endpoints
│   │   │       ├── attendance.py   # Attendance endpoints
│   │   │       └── dashboard.py    # Dashboard statistics
│   │   ├── core/
│   │   │   ├── config.py      # App configuration
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # JWT & password utilities
│   │   ├── models/
│   │   │   ├── user.py        # User model
│   │   │   ├── employee.py    # Employee model
│   │   │   ├── department.py  # Department model
│   │   │   └── attendance.py  # Attendance model
│   │   ├── schemas/
│   │   │   ├── auth.py        # Auth request/response schemas
│   │   │   ├── employee.py    # Employee schemas
│   │   │   ├── department.py  # Department schemas
│   │   │   └── attendance.py  # Attendance schemas
│   │   └── main.py            # FastAPI application entry point
│   ├── seed_data.py           # Database seed script
│   ├── requirements.txt       # Python dependencies
│   ├── alembic.ini            # Alembic configuration
│   ├── vercel.json            # Vercel backend config
│   └── .env.example           # Environment variables template
├── frontend/
│   ├── public/
│   │   └── favicon.svg        # App icon
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Loading.jsx       # Loading spinner
│   │   │   │   └── ProtectedRoute.jsx # Auth guard
│   │   │   └── layout/
│   │   │       ├── Layout.jsx        # Main layout wrapper
│   │   │       ├── Navbar.jsx        # Top navigation bar
│   │   │       └── Sidebar.jsx       # Side navigation
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx       # Authentication context
│   │   ├── hooks/
│   │   │   └── useAuth.js            # Auth hook
│   │   ├── pages/
│   │   │   ├── Login.jsx             # Login page
│   │   │   ├── Register.jsx          # Registration page
│   │   │   ├── Dashboard.jsx         # Dashboard with charts
│   │   │   ├── Employees.jsx         # Employee list
│   │   │   ├── EmployeeForm.jsx      # Add/Edit employee
│   │   │   ├── Departments.jsx       # Department management
│   │   │   ├── Attendance.jsx        # Attendance tracking
│   │   │   └── Profile.jsx           # User profile
│   │   ├── services/
│   │   │   ├── api.js                # Axios instance
│   │   │   ├── authService.js        # Auth API calls
│   │   │   ├── employeeService.js    # Employee API calls
│   │   │   ├── departmentService.js  # Department API calls
│   │   │   ├── attendanceService.js  # Attendance API calls
│   │   │   └── dashboardService.js   # Dashboard API calls
│   │   ├── utils/
│   │   │   └── constants.js          # App constants
│   │   ├── App.css                   # Global styles
│   │   ├── App.jsx                   # Route definitions
│   │   └── main.jsx                  # Entry point
│   ├── index.html                    # HTML template
│   ├── package.json                  # Node dependencies
│   ├── vite.config.js                # Vite configuration
│   └── .env.example                  # Frontend env template
├── .github/
│   └── workflows/
│       └── ci-cd.yml                 # CI/CD pipeline
├── vercel.json                       # Vercel frontend config
├── .gitignore
└── README.md
```

## Database Schema

### Users Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| username | VARCHAR(100) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| is_active | BOOLEAN | DEFAULT TRUE |
| is_superuser | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

### Departments Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(100) | UNIQUE, NOT NULL |
| description | TEXT | |
| manager_id | UUID | FK -> employees.id |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

### Employees Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| employee_id | VARCHAR(10) | UNIQUE, NOT NULL |
| user_id | UUID | FK -> users.id |
| department_id | UUID | FK -> departments.id |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| phone | VARCHAR(20) | |
| position | VARCHAR(100) | |
| salary | DECIMAL(12,2) | |
| date_of_birth | DATE | |
| date_of_hire | DATE | |
| address | TEXT | |
| city | VARCHAR(100) | |
| state | VARCHAR(50) | |
| zip_code | VARCHAR(10) | |
| status | VARCHAR(20) | DEFAULT 'active' |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

### Attendance Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| employee_id | UUID | FK -> employees.id |
| date | DATE | NOT NULL |
| check_in | TIMESTAMP | |
| check_out | TIMESTAMP | |
| status | VARCHAR(20) | DEFAULT 'present' |
| notes | TEXT | |

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get JWT | No |
| GET | `/api/auth/me` | Get current user profile | Yes |
| PUT | `/api/auth/me` | Update current user profile | Yes |

### Employee Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/employees` | List employees (search, filter, paginate, sort) | Yes |
| POST | `/api/employees` | Create new employee | Yes |
| GET | `/api/employees/{id}` | Get employee by ID | Yes |
| PUT | `/api/employees/{id}` | Update employee | Yes |
| DELETE | `/api/employees/{id}` | Soft delete employee | Yes |

**Query Parameters for GET /api/employees:**
- `search` - Search across name, email, position, employee_id
- `department_id` - Filter by department
- `status` - Filter by status (active/inactive/terminated)
- `page` - Page number (default: 1)
- `size` - Page size (default: 10, max: 100)
- `sort_by` - Sort column (default: created_at)
- `sort_order` - Sort direction: asc/desc (default: desc)

### Department Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/departments` | List all departments with employee count | Yes |
| POST | `/api/departments` | Create new department | Yes |
| GET | `/api/departments/{id}` | Get department details | Yes |
| PUT | `/api/departments/{id}` | Update department | Yes |
| DELETE | `/api/departments/{id}` | Delete department (must be empty) | Yes |

### Attendance Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/attendance` | List attendance records | Yes |
| POST | `/api/attendance` | Check in | Yes |
| PUT | `/api/attendance/{id}` | Check out | Yes |
| GET | `/api/attendance/today` | Get today's attendance | Yes |
| GET | `/api/attendance/summary` | Get attendance summary | Yes |

### Dashboard Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/dashboard/stats` | Get overview statistics | Yes |
| GET | `/api/dashboard/attendance-chart` | Last 30 days attendance data | Yes |
| GET | `/api/dashboard/department-distribution` | Employee count per department | Yes |
| GET | `/api/dashboard/recent-employees` | Last 5 employees added | Yes |

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (or SQLite for development)
- Git

### Clone the Repository

```bash
git clone https://github.com/yourusername/employee-management-system.git
cd employee-management-system
```

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

5. Create the database:
```bash
# PostgreSQL
createdb ems_db

# Or use SQLite by changing DATABASE_URL in .env to:
# DATABASE_URL=sqlite:///./ems.db
```

6. Run database migrations:
```bash
alembic upgrade head
```

7. Seed the database with sample data:
```bash
python seed_data.py
```

8. Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Update VITE_API_URL if needed (default: http://localhost:8000)
```

4. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### Default Accounts (after seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@ems.com | admin123 |
| Manager | manager@ems.com | manager123 |

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/ems_db` |
| `SECRET_KEY` | JWT signing secret | `your-super-secret-key-change-in-production` |
| `ALGORITHM` | JWT encryption algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |

## Running Locally

### Development Mode

1. Start the backend server:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

2. In a new terminal, start the frontend:
```bash
cd frontend
npm run dev
```

3. Open `http://localhost:3000` in your browser.

### Production Build

```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
cd frontend
npm run build
npm run preview
```

## GitHub Repository Setup

1. Create a new repository on GitHub.

2. Initialize the local repository and push:
```bash
cd employee-management-system
git init
git add .
git commit -m "Initial commit: Employee Management System"
git branch -M main
git remote add origin https://github.com/yourusername/employee-management-system.git
git push -u origin main
```

3. Configure GitHub Secrets for CI/CD:
   - Go to Settings > Secrets and variables > Actions
   - Add `VERCEL_TOKEN` - Your Vercel API token
   - Add `VERCEL_ORG_ID` - Your Vercel organization ID
   - Add `VERCEL_PROJECT_ID` - Your Vercel project ID

## CI/CD Workflow

The project includes a GitHub Actions workflow (`.github/workflows/ci-cd.yml`) that:

1. **Triggers**: Runs on push/PR to `main` or `master` branches.

2. **Backend Job**:
   - Sets up Python 3.11 with pip caching
   - Installs dependencies from `requirements.txt`
   - Lints with flake8 (error-checking and complexity checks)
   - Checks formatting with black
   - Verifies the FastAPI app can be imported

3. **Frontend Job**:
   - Sets up Node.js 20 with npm caching
   - Installs dependencies with `npm ci`
   - Lints with ESLint
   - Builds the production bundle with `npm run build`

4. **Deploy Job** (runs after both checks pass on main/master):
   - Deploys to Vercel using `amondnet/vercel-action`
   - Requires `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` secrets

## Deployment

### Deploy Frontend to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel --prod
```

Or connect your GitHub repository to Vercel for automatic deployments:
- Go to [vercel.com](https://vercel.com)
- Import your GitHub repository
- Set the root directory to `frontend`
- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Add environment variables from `frontend/.env.example`

### Deploy Backend to Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Deploy:
```bash
railway login
railway init
railway up
```

Or connect your GitHub repository:
- Go to [railway.app](https://railway.app)
- Create a new project from your repository
- Add a PostgreSQL database plugin
- Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add environment variables from `backend/.env.example`

### Deploy Backend to Render

1. Create a new Web Service on [render.com](https://render.com)
2. Connect your GitHub repository
3. Set:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `backend/.env.example`
5. Add a PostgreSQL database from the Render dashboard

## Future Enhancements

- [ ] Email notifications for attendance reminders
- [ ] Role-based access control with granular permissions
- [ ] File upload for employee documents and profile pictures
- [ ] Advanced reporting with CSV/PDF export
- [ ] Leave management system
- [ ] Performance review module
- [ ] Payroll integration
- [ ] Real-time notifications with WebSockets
- [ ] Mobile app with React Native
- [ ] Dark mode theme
- [ ] OAuth2 social login (Google, GitHub)
- [ ] Audit logging for all data changes
- [ ] Multi-language support (i18n)

## Troubleshooting Guide

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`
**Solution**: Run commands from the `backend/` directory, not the project root.

**Problem**: `psycopg2` installation fails
**Solution**: Install PostgreSQL development headers or use `pip install psycopg2-binary` instead.

**Problem**: Database connection refused
**Solution**: Ensure PostgreSQL is running and the credentials in `.env` are correct. For local development, you can use SQLite: `DATABASE_URL=sqlite:///./ems.db`.

**Problem**: Alembic migration fails
**Solution**: Run `alembic stamp head` to mark migrations as current, or delete the versions and run `alembic revision --autogenerate`.

### Frontend Issues

**Problem**: API calls return 401 Unauthorized
**Solution**: Clear localStorage and log in again. The token may have expired.

**Problem**: CORS errors in browser
**Solution**: Ensure the backend server is running and the proxy in `vite.config.js` is correctly configured.

**Problem**: Build fails with "Module not found"
**Solution**: Run `npm install` to ensure all dependencies are installed.

**Problem**: Charts not rendering
**Solution**: Check that `recharts` is installed and the API returns valid data.

### Deployment Issues

**Problem**: Vercel deployment shows blank page
**Solution**: Check the build logs. Ensure the `vercel.json` rewrites rule is correct for SPA routing.

**Problem**: Backend API returns 502 Bad Gateway
**Solution**: Check the server logs. The start command or `requirements.txt` may need adjustment.

**Problem**: Database data not persisting
**Solution**: Ensure you're using a managed PostgreSQL database (Railway/Render provide these) and not a local database that resets on restart.

## License

MIT License - see [LICENSE](LICENSE) file for details.
